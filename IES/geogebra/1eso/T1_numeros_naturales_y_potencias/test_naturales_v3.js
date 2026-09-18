/* Run after the JavaScript embedded in the generated .ggb. No browser APIs. */
(function () {
    var count = 0;
    function assert(value, message) { if (!value) throw new Error(message || "Assertion failed"); }
    function equal(a, b) { assert(JSON.stringify(a) === JSON.stringify(b), JSON.stringify(a) + " != " + JSON.stringify(b)); }
    function test(name, fn) { fn(); count++; print("OK " + name); }
    function fresh(groups, seconds) {
        var g = new NaturalesGame(NATURALES_BANK, function () { return 0; });
        g.settings.groups = groups || 3;
        g.settings.seconds = seconds === undefined ? 30 : seconds;
        g.dispatch("start");
        return g;
    }
    function correct(g) { return g.bank[g.question].correct; }
    function wrong(g) {
        for (var i = 0; i < 4; i++) {
            if (i !== correct(g) && g.excluded.indexOf(i) === -1) return i;
        }
    }
    function offer() {
        var g = fresh();
        g.answer(wrong(g));
        g.dispatch("next");
        g.answer(wrong(g));
        equal(g.phase, "offer");
        return g;
    }
    function rescue(g) { g.dispatch("choose"); g.dispatch("rescue", 0); }

    test("one point per answer, duplicate answers ignored", function () {
        var g = fresh(); g.answer(correct(g)); g.answer(correct(g));
        equal(g.teams[0].score, 1); equal(g.phase, "closed");
        g.dispatch("next"); equal(g.turn, 1);
        g.dispatch("next"); equal(g.turn, 1);
    });
    test("timeout eliminates and locks the answer exactly once", function () {
        var g = fresh(3, 5); g.tick(4.95); assert(g.teams[0].alive);
        g.tick(5); assert(!g.teams[0].alive); equal(g.phase, "closed");
        g.answer(correct(g)); g.tick(7); equal(g.teams[0].score, 0);
    });
    test("unlimited time does not expire or consume extra time", function () {
        var g = fresh(3, 0); g.tick(9999); g.help("time");
        equal(g.phase, "active"); assert(g.teams[0].time); equal(g.limit, 0);
    });
    test("extra time preserves elapsed time and is used once", function () {
        var g = fresh(3, 5); g.tick(4); g.help("time");
        equal(g.elapsed, 4); equal(g.limit, 25); assert(!g.teams[0].time);
        g.help("time"); equal(g.limit, 25); g.tick(24.9); assert(g.teams[0].alive);
        g.tick(25); assert(!g.teams[0].alive);
    });
    test("extra time configured independently before start", function () {
        var g = new NaturalesGame(NATURALES_BANK);
        g.dispatch("extra", 15); g.dispatch("seconds", -25); g.dispatch("start");
        g.help("time"); equal(g.limit, 40);
        g.dispatch("extra", 100); equal(g.settings.extra, 35);
    });
    test("settings remain inside their ranges", function () {
        var g = new NaturalesGame(NATURALES_BANK);
        g.dispatch("groups", 999); equal(g.settings.groups, 8);
        g.dispatch("groups", -999); equal(g.settings.groups, 2);
        g.dispatch("seconds", -999); equal(g.settings.seconds, 0);
        g.dispatch("seconds", 999); equal(g.settings.seconds, 120);
        g.dispatch("extra", -999); equal(g.settings.extra, 5);
        g.dispatch("extra", 999); equal(g.settings.extra, 120);
    });
    test("pass is independent per team and draws a fresh question", function () {
        var g = fresh(), q = g.question; g.help("pass");
        equal(g.turn, 1); assert(g.question !== q); assert(!g.teams[0].pass);
        assert(g.teams[1].pass); equal(g.teams[0].score, 0);
        g.answer(correct(g)); g.dispatch("next"); g.answer(correct(g)); g.dispatch("next");
        equal(g.turn, 0); q = g.question; g.help("pass"); equal(g.question, q);
    });
    test("remove never discards the correct answer for any question", function () {
        for (var q = 0; q < NATURALES_BANK.length; q++) {
            var g = fresh(); g.question = q; g.help("remove");
            equal(g.excluded.length, 1); assert(g.excluded[0] !== correct(g));
            g.answer(g.excluded[0]); equal(g.phase, "active");
            g.help("remove"); equal(g.excluded.length, 1);
        }
    });
    test("discarded option is reset on the next question", function () {
        var g = fresh(); g.help("remove"); g.help("pass"); equal(g.excluded, []);
        assert(!g.teams[0].remove); assert(g.teams[1].remove);
    });
    test("pause blocks all gameplay and preserves the timer", function () {
        var g = fresh(); g.tick(12.5); g.dispatch("pause");
        var snapshot = JSON.stringify(g);
        g.tick(99); g.answer(correct(g)); g.help("pass"); g.help("time");
        g.help("remove"); g.dispatch("next"); g.dispatch("requestReset");
        equal(JSON.stringify(g), snapshot);
        g.dispatch("pause"); g.tick(13); equal(g.elapsed, 13);
    });
    test("offer remains available when only one team survives", function () {
        var g = offer(); equal(g.living(), [2]); equal(g.eligible, [0]);
        g.dispatch("next"); equal(g.phase, "offer");
        g.dispatch("rescue", 1); equal(g.phase, "offer");
    });
    test("rebound keeps the same question and both discarded options", function () {
        var g = fresh(); g.answer(wrong(g)); g.dispatch("next");
        g.help("remove"); g.help("time"); g.tick(7);
        var q = g.question, discarded = g.excluded[0], bad = wrong(g);
        g.answer(bad); rescue(g);
        equal(g.phase, "rescue"); equal(g.question, q);
        equal(g.excluded, [discarded, bad]); equal(g.elapsed, 0); equal(g.limit, 30);
        assert(!g.teams[0].revive); assert(!g.teams[0].alive);
        g.answer(discarded); g.answer(bad); equal(g.phase, "rescue");
    });
    test("successful revival retains points and removes all original helps", function () {
        var g = fresh(); g.teams[0].score = 4;
        g.answer(wrong(g)); g.dispatch("next"); g.answer(wrong(g)); rescue(g);
        g.answer(correct(g)); equal(g.teams[0].score, 5); assert(g.teams[0].alive);
        assert(!g.teams[0].pass && !g.teams[0].time && !g.teams[0].remove);
        equal(g.actor(), 0); equal(g.phase, "closed");
        g.dispatch("next"); equal(g.turn, 2);
        g.answer(correct(g)); g.dispatch("next"); equal(g.turn, 0);
        g.help("time"); equal(g.limit, 30);
    });
    test("failed revival cannot be repeated or chained", function () {
        var g = offer(); rescue(g); g.answer(wrong(g));
        equal(g.phase, "closed"); assert(!g.teams[0].alive); assert(!g.teams[0].revive);
        g.dispatch("choose"); equal(g.phase, "closed");
        g.dispatch("next"); equal(g.phase, "over");
    });
    test("a revived team cannot revive a second time", function () {
        var g = offer(); rescue(g); g.answer(correct(g)); g.dispatch("next");
        g.answer(correct(g)); g.dispatch("next"); g.answer(wrong(g));
        assert(g.eligible.indexOf(0) === -1); assert(!g.teams[0].revive);
    });
    test("revival cannot consume any initial help", function () {
        var g = offer(); rescue(g); var snapshot = JSON.stringify(g);
        g.help("pass"); g.help("remove"); g.help("time"); equal(JSON.stringify(g), snapshot);
    });
    test("pause and expiration during revival", function () {
        var g = offer(); rescue(g); g.tick(8); g.dispatch("pause"); g.tick(100);
        equal(g.elapsed, 8); assert(!g.teams[0].alive);
        g.dispatch("pause"); g.tick(30); equal(g.phase, "closed"); assert(!g.teams[0].alive);
    });
    test("normal timeout can offer a revival without discarding an answer", function () {
        var g = fresh(); g.answer(wrong(g)); g.dispatch("next"); g.tick(30);
        equal(g.phase, "offer"); equal(g.excluded, []); rescue(g); equal(g.phase, "rescue");
    });
    test("declining revival reveals before ending the match", function () {
        var g = offer(); g.dispatch("reveal"); equal(g.phase, "closed");
        assert(g.teams[0].revive); g.dispatch("next"); equal(g.phase, "over");
    });
    test("invalid team selections cannot revive a living or ineligible team", function () {
        var g = offer(); g.dispatch("choose");
        g.dispatch("rescue", 2); g.dispatch("rescue", 1); g.dispatch("rescue", -1);
        equal(g.phase, "choosing"); g.dispatch("rescue", 0); equal(g.phase, "rescue");
        g.dispatch("rescue", 0); assert(!g.teams[0].revive);
    });
    test("full bank is used once before replenishing", function () {
        var g = fresh(), seen = {};
        for (var i = 0; i < NATURALES_BANK.length; i++) {
            assert(!seen[g.question]); seen[g.question] = true;
            g.answer(correct(g)); g.dispatch("next");
        }
        equal(Object.keys(seen).length, NATURALES_BANK.length);
        equal(g.pending.length, NATURALES_BANK.length - 1);
    });
    test("restart confirmation freezes time; reset restores teams and helps", function () {
        var g = fresh(); g.help("time"); g.tick(4); g.dispatch("requestReset");
        g.tick(100); equal(g.elapsed, 4); g.answer(correct(g)); equal(g.teams[0].score, 0);
        g.dispatch("cancelReset"); equal(g.elapsed, 4);
        g.dispatch("requestReset"); g.dispatch("reset"); equal(g.phase, "setup");
        g.dispatch("start"); equal(g.round, 1);
        assert(g.teams.every(function (t) { return t.alive && t.pass && t.time && t.remove && t.revive && t.score === 0; }));
    });
    test("zero survivors is handled without an undefined winner", function () {
        var g = fresh(2); g.teams.forEach(function (t) { t.alive = false; });
        g.phase = "closed"; g.dispatch("next"); equal(g.phase, "over");
        assert(g.message.indexOf("undefined") === -1);
    });

    function fakeAPI() {
        var values = {reloj: 0}, visible = {}, strings = {}, colors = {}, backgrounds = {}, positions = {}, callbacks = {};
        function exists(name) { assert(name === "reloj" || NATURALES_UI.indexOf(name) !== -1, "Unknown object: " + name); }
        return {
            visible: visible, strings: strings, colors: colors, backgrounds: backgrounds, positions: positions, running: false,
            setValue: function (n, v) { exists(n); values[n] = v; if (callbacks[n]) callbacks[n](); },
            getValue: function (n) { exists(n); return values[n]; },
            setVisible: function (n, v) { exists(n); visible[n] = v; },
            setTextValue: function (n, v) { exists(n); strings[n] = v; },
            setColor: function (n, r, g, b) { exists(n); colors[n] = [r, g, b]; },
            evalCommand: function (command) {
                var coords = /^SetCoords\((\w+), (\d+), (\d+)\)$/.exec(command);
                if (coords) {
                    exists(coords[1]); positions[coords[1]] = [Number(coords[2]), Number(coords[3])]; return true;
                }
                var match = /^SetBackgroundColor\((\w+), "(#[0-9A-F]{6})"\)$/.exec(command);
                assert(match, "Expected an unambiguous hexadecimal color: " + command);
                exists(match[1]); backgrounds[match[1]] = match[2]; return true;
            },
            setAnimating: function (n, v) { exists(n); this.animating = v; },
            startAnimation: function () { this.running = true; },
            stopAnimation: function () { this.running = false; },
            setRepaintingActive: function (v) { this.repaint = v; },
            registerObjectUpdateListener: function (n, fn) { exists(n); equal(fn, "naturalesClock"); callbacks[n] = naturalesClock; }
        };
    }
    test("native clock callbacks eliminate without browser timer APIs", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("seconds", -25); NV3.dispatch("start");
        api.setValue("reloj", 5); equal(NV3.game.phase, "closed");
        assert(!NV3.game.teams[0].alive); assert(!api.running); assert(api.repaint);
    });
    test("clock reset on next question does not trigger a stale timeout", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start"); api.setValue("reloj", 30);
        NV3.dispatch("next"); equal(NV3.game.phase, "active"); equal(api.getValue("reloj"), 0);
        equal(NV3.game.elapsed, 0); assert(api.running);
    });
    test("only resume is visible during pause; no state is lost", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start"); api.setValue("reloj", 8);
        NV3.dispatch("pause");
        equal(NATURALES_UI.filter(function (name) { return api.visible[name]; }), ["resume"]);
        assert(!api.running); NV3.dispatch("answer", correct(NV3.game)); equal(NV3.game.teams[0].score, 0);
        NV3.dispatch("pause"); equal(NV3.game.elapsed, 8); assert(api.running);
    });
    test("correct option and explanation stay hidden during offer and selection", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start");
        NV3.dispatch("answer", wrong(NV3.game)); NV3.dispatch("next");
        NV3.dispatch("help", "remove"); NV3.dispatch("answer", wrong(NV3.game));
        equal(NV3.game.phase, "offer"); equal(api.strings.explanation, ""); assert(!api.visible.explanation);
        equal(api.colors["answer" + correct(NV3.game)], [36, 43, 48]);
        NV3.dispatch("choose"); assert(api.visible.choose0); assert(!api.visible.choose1);
        NV3.dispatch("rescue", 0); equal(api.strings.explanation, "");
        NV3.dispatch("answer", correct(NV3.game)); assert(api.visible.explanation);
        assert(api.strings.explanation.length > 0);
    });
    test("unlimited games never start the native animation", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("seconds", -30); NV3.dispatch("start");
        assert(!api.running); assert(api.visible.helpTimeOff); assert(!api.visible.helpTime);
    });
    test("failure uses a pale background and success has its own color", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start");
        NV3.dispatch("answer", wrong(NV3.game)); equal(api.backgrounds.status, "#F8E3E2");
        NV3.dispatch("next"); NV3.dispatch("answer", correct(NV3.game));
        equal(api.backgrounds.status, "#DEF0E4");
        equal(api.backgrounds["answer" + correct(NV3.game)], "#DAF0E1");
    });
    test("resting teams get a friendly message after an error or timeout", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start");
        NV3.dispatch("answer", wrong(NV3.game));
        assert(api.strings.team0.indexOf("Descanso") !== -1);
        assert(api.strings.status.indexOf("pasa a descansar") !== -1);
        assert(api.strings.status.indexOf("eliminado") === -1);
        assert(api.strings.team0.indexOf("Fuera") === -1);
        NV3.dispatch("next"); api.setValue("reloj", 30);
        assert(api.strings.team1.indexOf("Descanso") !== -1);
        assert(api.strings.status.indexOf("pasa a descansar") !== -1);
        NV3.dispatch("choose"); NV3.dispatch("rescue", 0);
        NV3.dispatch("answer", correct(NV3.game));
        assert(api.strings.team0.indexOf("Descanso") === -1);
    });
    test("large red countdown appears at ten, not eleven seconds", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start");
        api.setValue("reloj", 19.95); assert(api.visible.clock); assert(!api.visible.clockUrgent);
        api.setValue("reloj", 20); assert(!api.visible.clock); assert(api.visible.clockUrgent);
        equal(api.strings.clockUrgent, "10"); equal(api.colors.clockUrgent, NATURALES_COLORS.red);
        api.setValue("reloj", 29.5); equal(api.strings.clockUrgent, "1");
        api.setValue("reloj", 30); assert(!api.visible.clockUrgent); equal(api.strings.clock, "0");
        assert(!api.running); assert(!NV3.game.teams[0].alive);
    });
    test("extra time clears urgency without resetting the native clock", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start"); api.setValue("reloj", 22);
        assert(api.visible.clockUrgent); NV3.dispatch("help", "time");
        assert(!api.visible.clockUrgent); equal(api.strings.clock, "28");
        equal(api.getValue("reloj"), 22); equal(NV3.game.elapsed, 22);
        api.setValue("reloj", 40); assert(api.visible.clockUrgent); equal(api.strings.clockUrgent, "10");
    });
    test("short challenges start urgent; unlimited games never do", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("seconds", -25); NV3.dispatch("start");
        assert(api.visible.clockUrgent); equal(api.strings.clockUrgent, "5");
        NV3.dispatch("requestReset"); NV3.dispatch("reset"); NV3.dispatch("seconds", -5); NV3.dispatch("start");
        assert(!api.visible.clockUrgent); assert(api.visible.clockUnlimited); assert(!api.visible.clockUnit);
        assert(!api.visible.helpTimeUsed); assert(api.visible.helpTimeOff);
        assert(api.visible.team0_timeOff); assert(NV3.game.teams[0].time);
    });
    test("pause and reset confirmation hide the urgent clock without losing time", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start"); api.setValue("reloj", 25);
        NV3.dispatch("pause"); assert(!api.visible.clockUrgent); assert(!api.running);
        NV3.dispatch("pause"); equal(api.strings.clockUrgent, "5"); assert(api.running);
        NV3.dispatch("requestReset"); assert(!api.visible.clockUrgent); assert(!api.running);
        NV3.dispatch("cancelReset"); assert(api.visible.clockUrgent); equal(api.getValue("reloj"), 25);
    });
    test("revival gets its own urgency and disabled, not falsely spent, controls", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start");
        NV3.dispatch("answer", wrong(NV3.game)); NV3.dispatch("next");
        NV3.dispatch("answer", wrong(NV3.game)); NV3.dispatch("choose"); NV3.dispatch("rescue", 0);
        assert(api.visible.helpPassOff); assert(!api.visible.helpPassUsed);
        assert(api.visible.team0_reviveUsed); assert(!api.visible.team0_revive);
        api.setValue("reloj", 20); assert(api.visible.clockUrgent);
        NV3.dispatch("answer", correct(NV3.game)); assert(!api.visible.clockUrgent);
        ["pass", "time", "remove", "revive"].forEach(function (kind) { assert(api.visible["team0_" + kind + "Used"]); });
    });
    test("spent controls have crosses on the board and in the scoreboard", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start");
        NV3.dispatch("help", "time"); assert(api.visible.helpTimeUsed); assert(!api.visible.helpTimeOff);
        assert(api.visible.team0_timeUsed); equal(api.strings.extraAmount, "Usado");
        equal(api.colors.extraAmount, NATURALES_COLORS.red);
        NV3.dispatch("help", "remove"); assert(api.visible.helpRemoveUsed); assert(api.visible.team0_removeUsed);
        NV3.dispatch("help", "pass"); assert(api.visible.team0_passUsed); assert(api.visible.helpPass);
        for (var i = 0; i < 4; i++) { NV3.dispatch("answer", correct(NV3.game)); NV3.dispatch("next"); }
        equal(NV3.game.turn, 0); assert(api.visible.helpPassUsed); assert(api.visible.helpTimeUsed);
        assert(api.visible.helpRemoveUsed); assert(!api.visible.helpRemove);
    });
    test("resting teams retain unused gray helps, with consumed ones crossed out", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start");
        NV3.dispatch("help", "time"); NV3.dispatch("answer", wrong(NV3.game));
        assert(api.visible.team0_timeUsed); assert(api.visible.team0_passOff);
        assert(api.visible.team0_removeOff); assert(!api.visible.team0_passUsed);
        assert(api.visible.team0_revive);
    });
    test("discarded answers have a cross, strong contrast and cannot be selected", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start"); NV3.dispatch("help", "remove");
        var g = NV3.game, discarded = g.excluded[0];
        assert(api.visible["discard" + discarded]); equal(api.colors["answer" + discarded], NATURALES_COLORS.red);
        equal(api.backgrounds["answer" + discarded], "#FAE2E5");
        equal(api.colors["answer" + correct(g)], NATURALES_COLORS.ink);
        NV3.dispatch("answer", discarded); equal(g.phase, "active");
        NV3.dispatch("help", "pass");
        for (var i = 0; i < 4; i++) assert(!api.visible["discard" + i]);
    });
    test("both discarded answers stay marked throughout a revival", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start");
        NV3.dispatch("answer", wrong(NV3.game)); NV3.dispatch("next"); NV3.dispatch("help", "remove");
        NV3.dispatch("answer", wrong(NV3.game)); NV3.dispatch("choose"); NV3.dispatch("rescue", 0);
        equal(NV3.game.excluded.length, 2);
        NV3.game.excluded.forEach(function (i) { assert(api.visible["discard" + i]); });
        assert(!api.visible["discard" + correct(NV3.game)]); equal(api.strings.explanation, "");
    });
    test("all tied leaders receive trophies, which move with the score", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start");
        for (var i = 0; i < 5; i++) assert(!api.visible["teamCup" + i]);
        NV3.dispatch("answer", correct(NV3.game)); assert(api.visible.teamCup0); assert(!api.visible.teamCup1);
        NV3.dispatch("next"); NV3.dispatch("answer", correct(NV3.game));
        assert(api.visible.teamCup0 && api.visible.teamCup1); assert(!api.visible.teamCup2);
        NV3.game.teams[1].score++; NV3.render(); assert(!api.visible.teamCup0); assert(api.visible.teamCup1);
    });
    test("highest score wins even when that team rests; end waits for revival decisions", function () {
        var g = fresh(); g.teams[0].score = 5; g.teams[2].score = 1;
        g.answer(wrong(g)); g.dispatch("next"); g.answer(wrong(g));
        equal(g.phase, "offer"); g.dispatch("next"); equal(g.phase, "offer");
        g.dispatch("reveal"); g.dispatch("next"); equal(g.phase, "over");
        equal(g.leaders(), [0]); assert(g.message.indexOf("Grupo 1") !== -1);
    });
    test("final tied winners share trophies and a poster without stale question content", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start");
        var g = NV3.game; g.teams[0].score = g.teams[3].score = 4;
        g.teams.forEach(function (t, i) { t.alive = i === 2; }); g.phase = "closed"; NV3.render();
        assert(api.visible.next); assert(api.visible.finishGame); NV3.dispatch("next");
        equal(g.phase, "over"); assert(api.visible.winnerPoster); assert(api.visible.winnerCup);
        equal(api.strings.winnerName0, "Grupo 1"); equal(api.strings.winnerName1, "Grupo 4");
        equal(api.strings.winnerScore, "4 puntos"); assert(!api.visible.winnerName2);
        assert(api.visible.teamCup0 && api.visible.teamCup3 && !api.visible.teamCup2);
        ["question", "expression", "explanation", "answer0", "answer1", "answer2", "answer3",
            "clock", "clockUrgent", "clockFace", "clockFaceUrgent", "clockUnit", "clockUnlimited",
            "helpTime", "helpTimeUsed", "next", "finishGame"].forEach(function (n) { assert(!api.visible[n], n); });
        equal(api.strings.explanation, ""); assert(!api.running);
        var scores = JSON.stringify(g.teams); NV3.dispatch("answer", correct(g)); NV3.dispatch("help", "time");
        equal(JSON.stringify(g.teams), scores);
    });
    test("all eight teams can share first place, including a zero-point tie", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("groups", 3); NV3.dispatch("start");
        var g = NV3.game; g.teams.forEach(function (t, i) { t.alive = i === 7; });
        g.phase = "closed"; NV3.dispatch("next"); equal(g.leaders(), [0, 1, 2, 3, 4, 5, 6, 7]);
        for (var i = 0; i < 8; i++) {
            assert(api.visible["winnerName" + i] && api.visible["winnerBadge" + i] && api.visible["teamCup" + i]);
            equal(api.strings["winnerName" + i], "Grupo " + (i + 1));
        }
        equal(api.strings.winnerScore, "0 puntos"); assert(!api.visible.winnerSolo);
    });
    test("a sole winner is centered and the poster can be paused and reset", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start");
        var g = NV3.game; g.teams[2].score = 1;
        g.teams.forEach(function (t, i) { t.alive = i === 2; }); g.phase = "closed"; NV3.dispatch("next");
        equal(api.strings.winnerTitle, "Ganador"); equal(api.strings.winnerScore, "1 punto");
        equal(api.strings.winnerSolo, "Grupo 3"); assert(api.visible.winnerSoloBadge); assert(!api.visible.winnerName0);
        NV3.dispatch("pause"); equal(NATURALES_UI.filter(function (n) { return api.visible[n]; }), ["resume"]);
        NV3.dispatch("pause"); assert(api.visible.winnerPoster);
        NV3.dispatch("requestReset"); assert(!api.visible.winnerPoster); NV3.dispatch("cancelReset");
        assert(api.visible.winnerPoster); NV3.dispatch("requestReset"); NV3.dispatch("reset"); NV3.dispatch("start");
        assert(!api.visible.winnerPoster); assert(!api.visible.winnerSolo);
        for (var i = 0; i < 5; i++) assert(!api.visible["teamCup" + i]);
        assert(api.visible.helpTime); assert(!api.visible.helpTimeUsed);
    });
    test("teacher can browse the full bank without answering or spending helps", function () {
        var g = fresh(8, 0), teams = JSON.stringify(g.teams), seen = {};
        for (var i = 0; i < NATURALES_BANK.length; i++) {
            assert(!seen[g.question]); seen[g.question] = true;
            equal(g.turn, i % 8); g.dispatch("skip");
        }
        equal(Object.keys(seen).length, NATURALES_BANK.length);
        equal(g.pending.length, NATURALES_BANK.length - 1);
        equal(JSON.stringify(g.teams), teams); equal(g.round, NATURALES_BANK.length + 1);
    });
    test("skipping resets the native clock and exclusions, preserving spent helps", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start"); api.setValue("reloj", 12);
        NV3.dispatch("help", "time"); NV3.dispatch("help", "remove");
        var teams = JSON.stringify(NV3.game.teams); NV3.dispatch("skip");
        equal(JSON.stringify(NV3.game.teams), teams); equal(NV3.game.elapsed, 0);
        equal(api.getValue("reloj"), 0); equal(NV3.game.limit, 30); equal(NV3.game.excluded, []);
        equal(NV3.game.turn, 1); assert(api.running); assert(NV3.game.teams[0].pass);
    });
    test("teacher controls stay visible while active, closed, offering, choosing and rescuing", function () {
        var api = fakeAPI(); NV3.mount(api); assert(!api.visible.next && !api.visible.finishGame);
        function controls() { assert(api.visible.next && api.visible.finishGame); }
        NV3.dispatch("start"); controls();
        NV3.dispatch("answer", wrong(NV3.game)); equal(NV3.game.phase, "closed"); controls();
        NV3.dispatch("skip"); NV3.dispatch("answer", wrong(NV3.game)); equal(NV3.game.phase, "offer"); controls();
        assert(api.visible.reveal); NV3.dispatch("choose"); equal(NV3.game.phase, "choosing"); controls();
        NV3.dispatch("rescue", 0); equal(NV3.game.phase, "rescue"); controls();
        NV3.dispatch("pause"); assert(!api.visible.next && !api.visible.finishGame);
        NV3.dispatch("pause"); controls(); NV3.dispatch("requestReset");
        assert(!api.visible.next && !api.visible.finishGame);
    });
    test("skipping an offer declines without spending the unselected revival", function () {
        ["offer", "choosing"].forEach(function (phase) {
            var g = fresh(4); g.answer(wrong(g)); g.dispatch("next"); g.answer(wrong(g));
            if (phase === "choosing") g.dispatch("choose");
            equal(g.phase, phase); g.dispatch("skip"); equal(g.phase, "active"); equal(g.turn, 2);
            assert(g.teams[0].revive); equal(g.eligible, []); equal(g.excluded, []);
        });
    });
    test("skipping a selected revival does not revive or refund its chance", function () {
        var g = fresh(4); g.answer(wrong(g)); g.dispatch("next"); g.answer(wrong(g)); rescue(g);
        var teams = JSON.stringify(g.teams); g.dispatch("skip");
        equal(JSON.stringify(g.teams), teams); equal(g.turn, 2); equal(g.rescuer, -1);
        assert(!g.teams[0].alive && !g.teams[0].revive);
        var last = offer(); last.dispatch("skip"); equal(last.phase, "over");
    });
    test("skipping a closed correct answer neither duplicates nor removes its point", function () {
        var g = fresh(); g.answer(correct(g)); g.dispatch("skip");
        equal(g.teams[0].score, 1); equal(g.teams[1].score, 0); equal(g.turn, 1);
        g.dispatch("requestFinish"); g.dispatch("finish");
        var snapshot = JSON.stringify(g); g.dispatch("skip"); equal(JSON.stringify(g), snapshot);
    });
    test("ending early freezes the timer and can be cancelled without losing the question", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start"); api.setValue("reloj", 23.5);
        var g = NV3.game, before = JSON.stringify(g); NV3.dispatch("requestFinish");
        assert(g.confirmFinish && !g.running() && !api.running);
        equal(NATURALES_UI.filter(function (n) { return api.visible[n]; }).sort(),
            ["finishNo", "finishQuestion", "finishTitle", "finishYes"].sort());
        g.tick(99); NV3.dispatch("answer", correct(g)); NV3.dispatch("help", "pass");
        NV3.dispatch("skip"); NV3.dispatch("pause"); NV3.dispatch("requestReset");
        NV3.dispatch("cancelFinish"); equal(JSON.stringify(g), before);
        equal(api.getValue("reloj"), 23.5); assert(api.running); assert(api.visible.clockFaceUrgent);
    });
    test("ending at the bell keeps all scores and shows all tied winners immediately", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start");
        var g = NV3.game; g.teams[0].score = g.teams[3].score = 3;
        var teams = JSON.stringify(g.teams); NV3.dispatch("requestFinish"); NV3.dispatch("finish");
        equal(g.phase, "over"); equal(g.living().length, 5); equal(JSON.stringify(g.teams), teams);
        equal(g.leaders(), [0, 3]); assert(api.visible.winnerPoster && api.visible.teamCup0 && api.visible.teamCup3);
        assert(!api.running && !api.visible.next && !api.visible.finishGame);
        NV3.dispatch("answer", correct(g)); NV3.dispatch("skip"); equal(JSON.stringify(g.teams), teams);
    });
    test("finish works during an offer, a selection and a revival without awarding the pending answer", function () {
        ["offer", "choosing", "rescue"].forEach(function (phase) {
            var g = offer();
            if (phase !== "offer") g.dispatch("choose");
            if (phase === "rescue") g.dispatch("rescue", 0);
            equal(g.phase, phase); var before = JSON.stringify(g.teams);
            g.dispatch("requestFinish"); g.dispatch("finish"); equal(g.phase, "over");
            equal(JSON.stringify(g.teams), before); equal(g.eligible, []);
        });
    });
    test("finish requires confirmation and cannot bypass pause or reset", function () {
        var g = new NaturalesGame(NATURALES_BANK); g.dispatch("requestFinish");
        equal(g.phase, "setup"); assert(!g.confirmFinish); g.dispatch("start");
        g.dispatch("finish"); equal(g.phase, "active"); g.dispatch("pause");
        var before = JSON.stringify(g); g.dispatch("requestFinish"); g.dispatch("skip"); equal(JSON.stringify(g), before);
        g.dispatch("pause"); g.dispatch("requestReset"); before = JSON.stringify(g);
        g.dispatch("requestFinish"); g.dispatch("finish"); g.dispatch("skip"); equal(JSON.stringify(g), before);
        g.dispatch("cancelReset"); g.dispatch("requestFinish"); g.dispatch("finish");
        equal(g.leaders(), [0, 1, 2, 3, 4]); g.dispatch("requestReset"); g.dispatch("reset"); g.dispatch("start");
        assert(!g.confirmFinish); equal(g.phase, "active");
    });
    test("circle changes color with urgency and keeps one, two and three digits centered", function () {
        var api = fakeAPI(); NV3.mount(api); NV3.dispatch("seconds", 90); NV3.dispatch("extra", 100); NV3.dispatch("start");
        NV3.dispatch("help", "time"); equal(api.strings.clock, "240"); equal(api.positions.clock, [744, 108]);
        assert(api.visible.clockFace && !api.visible.clockFaceUrgent && api.visible.clockUnit);
        api.setValue("reloj", 200); equal(api.strings.clock, "40"); equal(api.positions.clock, [753, 108]);
        api.setValue("reloj", 230); equal(api.strings.clockUrgent, "10"); equal(api.positions.clockUrgent, [741, 114]);
        assert(api.visible.clockFaceUrgent && !api.visible.clockFace); equal(api.colors.clockUnit, NATURALES_COLORS.red);
        api.setValue("reloj", 239); equal(api.strings.clockUrgent, "1"); equal(api.positions.clockUrgent, [757, 114]);
        NV3.dispatch("pause"); assert(!api.visible.clockFaceUrgent && !api.visible.clockUnit);
        NV3.dispatch("pause"); assert(api.visible.clockFaceUrgent);
        NV3.dispatch("skip"); assert(api.visible.clockFace && !api.visible.clockFaceUrgent);
    });
    test("teacher clicks at an elapsed deadline cannot cancel an existing timeout", function () {
        var api = fakeAPI(), get = api.getValue; NV3.mount(api); NV3.dispatch("start");
        api.getValue = function (name) { return name === "reloj" ? 30 : get(name); };
        NV3.dispatch("skip"); assert(!NV3.game.teams[0].alive); equal(NV3.game.turn, 1);
        equal(NV3.game.phase, "active"); equal(NV3.game.elapsed, 0);
    });
    if (NATURALES_LEVELS.length) {
        function leveled(level) {
            var g = new NaturalesGame(NATURALES_BANK, function () { return 0; }, NATURALES_LEVELS);
            g.settings.seconds = 0;
            if (level !== undefined) g.dispatch("level", level);
            g.dispatch("start");
            return g;
        }
        test("each level draws fifteen distinct questions before refilling", function () {
            [1, 2, 3].forEach(function (level) {
                var g = leveled(level), seen = {};
                for (var i = 0; i < 15; i++) {
                    equal(g.bank[g.question].level, level); assert(!seen[g.question]);
                    seen[g.question] = true; g.dispatch("skip");
                }
                equal(Object.keys(seen).length, 15); equal(g.candidates().length, 14);
                equal(g.bank[g.question].level, level); equal(g.pending.length, 44);
                equal(g.pending.length, Object.keys(g.pending.reduce(function (set, k) { set[k] = true; return set; }, {})).length);
            });
        });
        test("All mixes all forty-five questions without repeats", function () {
            var g = leveled(0), seen = {}, levels = {};
            for (var i = 0; i < 45; i++) {
                assert(!seen[g.question]); seen[g.question] = true;
                levels[g.bank[g.question].level] = true; g.dispatch("skip");
            }
            equal(Object.keys(seen).length, 45); equal(Object.keys(levels).length, 3);
            equal(g.pending.length, 44); equal(g.candidates().length, 44);
        });
        test("changing levels only affects the next question", function () {
            var g = leveled(); g.settings.seconds = 30; g.limit = 30;
            g.help("remove"); g.tick(7); var before = JSON.stringify(g);
            g.dispatch("level", 3); var snapshot = JSON.parse(before); snapshot.level = 3;
            equal(g, snapshot); equal(g.bank[g.question].level, 1);
            g.dispatch("skip"); equal(g.bank[g.question].level, 3); equal(g.elapsed, 0);
            equal(g.turn, 1); assert(!g.teams[0].remove && g.teams[0].pass);
        });
        test("switching away and back retains unasked questions", function () {
            var g = leveled(1), first = g.question;
            g.dispatch("level", 2); g.dispatch("skip"); var second = g.question;
            g.dispatch("level", 1); g.dispatch("skip");
            assert(g.question !== first); assert(g.pending.indexOf(first) === -1);
            assert(g.pending.indexOf(second) === -1); equal(g.pending.length, 42);
            equal(g.candidates().length, 13);
        });
        test("refilling an exhausted level does not refill other levels", function () {
            var g = leveled(2), used = g.question;
            g.dispatch("level", 1);
            for (var i = 0; i < 16; i++) g.dispatch("skip");
            equal(g.bank[g.question].level, 1); equal(g.candidates().length, 14);
            assert(g.pending.indexOf(used) === -1);
            equal(g.pending.filter(function (i) { return g.bank[i].level === 2; }).length, 14);
            equal(g.pending.filter(function (i) { return g.bank[i].level === 3; }).length, 15);
            equal(g.pending.length, 43);
        });
        test("invalid and repeated selections cannot reset the question or clock", function () {
            var g = leveled(2), before = JSON.stringify(g);
            [2, -1, 4, 1.5, "1", null, undefined, NaN, Infinity].forEach(function (level) { g.dispatch("level", level); });
            equal(JSON.stringify(g), before);
        });
        test("level selection cannot replace the failed question during revival", function () {
            var g = leveled(1); g.answer(wrong(g)); g.dispatch("next");
            g.help("remove"); g.answer(wrong(g)); equal(g.phase, "offer");
            var question = g.question, excluded = g.excluded.slice(0);
            g.dispatch("level", 3); g.dispatch("choose"); g.dispatch("level", 2); g.dispatch("rescue", 0);
            equal(g.phase, "rescue"); equal(g.question, question); equal(g.excluded, excluded);
            equal(g.bank[g.question].level, 1); g.answer(correct(g)); g.dispatch("skip");
            equal(g.bank[g.question].level, 2); equal(g.teams[0].score, 1);
        });
        test("pause and both confirmations block level changes", function () {
            var g = leveled(2); g.dispatch("pause"); g.dispatch("level", 3); equal(g.level, 2);
            g.dispatch("pause"); g.dispatch("requestReset"); g.dispatch("level", 1); equal(g.level, 2);
            g.dispatch("cancelReset"); g.dispatch("requestFinish"); g.dispatch("level", 0); equal(g.level, 2);
            g.dispatch("cancelFinish"); g.dispatch("level", 3); equal(g.level, 3);
        });
        test("restart retains the chosen level and resets its question pool", function () {
            var g = leveled(3); g.answer(correct(g)); g.dispatch("skip");
            g.dispatch("requestReset"); g.dispatch("reset"); equal(g.level, 3); g.dispatch("start");
            equal(g.bank[g.question].level, 3); equal(g.candidates().length, 14);
            equal(g.pending.length, 44); equal(g.round, 1); equal(g.teams[0].score, 0);
        });
        test("setup highlights level one and selected level matches the first question", function () {
            var api = fakeAPI(); NV3.mount(api); equal(NV3.game.level, 1);
            [0, 1, 2, 3].forEach(function (level) { assert(api.visible["level" + level]); });
            equal(api.backgrounds.level1, "#2A5B64"); equal(api.colors.level1, NATURALES_COLORS.paper);
            NV3.dispatch("level", 3); equal(api.backgrounds.level3, "#2A5B64");
            equal(api.backgrounds.level1, "#FAFBFC"); NV3.dispatch("start");
            equal(NV3.game.bank[NV3.game.question].level, 3);
        });
        test("pending count follows selected level without changing the current question", function () {
            var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start"); api.setValue("reloj", 12);
            var q = NV3.game.question; assert(api.strings.round.indexOf("14 pendientes") !== -1);
            NV3.dispatch("level", 2); equal(NV3.game.question, q); equal(NV3.game.elapsed, 12);
            assert(api.strings.round.indexOf("15 pendientes") !== -1);
            NV3.dispatch("skip"); equal(NV3.game.bank[NV3.game.question].level, 2);
            assert(api.strings.round.indexOf("14 pendientes") !== -1); equal(api.getValue("reloj"), 0);
        });
        test("level selector is hidden throughout pause, confirmations and results", function () {
            var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start");
            function hidden() { [0, 1, 2, 3].forEach(function (level) { assert(!api.visible["level" + level]); }); }
            NV3.dispatch("pause"); hidden();
            equal(NATURALES_UI.filter(function (n) { return api.visible[n]; }), ["resume"]);
            NV3.dispatch("pause"); assert(api.visible.level1);
            NV3.dispatch("requestReset"); hidden(); NV3.dispatch("cancelReset");
            NV3.dispatch("requestFinish"); hidden(); NV3.dispatch("finish"); hidden();
            var level = NV3.game.level; NV3.dispatch("level", 3); equal(NV3.game.level, level);
        });
    } else {
        test("games without levels ignore level actions and do not add selectors", function () {
            var api = fakeAPI(); NV3.mount(api); NV3.dispatch("start"); var before = JSON.stringify(NV3.game);
            NV3.dispatch("level", 1); equal(JSON.stringify(NV3.game), before);
            equal(NATURALES_UI.filter(function (n) { return /^level[0-9]+$/.test(n); }), []);
        });
    }
    print("PASS: " + count + " tests");
})();
