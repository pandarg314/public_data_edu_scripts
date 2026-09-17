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
        var values = {reloj: 0}, visible = {}, strings = {}, colors = {}, backgrounds = {}, callbacks = {};
        function exists(name) { assert(name === "reloj" || NATURALES_UI.indexOf(name) !== -1, "Unknown object: " + name); }
        return {
            visible: visible, strings: strings, colors: colors, backgrounds: backgrounds, running: false,
            setValue: function (n, v) { exists(n); values[n] = v; if (callbacks[n]) callbacks[n](); },
            getValue: function (n) { exists(n); return values[n]; },
            setVisible: function (n, v) { exists(n); visible[n] = v; },
            setTextValue: function (n, v) { exists(n); strings[n] = v; },
            setColor: function (n, r, g, b) { exists(n); colors[n] = [r, g, b]; },
            evalCommand: function (command) {
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
        var api = fakeAPI(); NV2.mount(api); NV2.dispatch("seconds", -25); NV2.dispatch("start");
        api.setValue("reloj", 5); equal(NV2.game.phase, "closed");
        assert(!NV2.game.teams[0].alive); assert(!api.running); assert(api.repaint);
    });
    test("clock reset on next question does not trigger a stale timeout", function () {
        var api = fakeAPI(); NV2.mount(api); NV2.dispatch("start"); api.setValue("reloj", 30);
        NV2.dispatch("next"); equal(NV2.game.phase, "active"); equal(api.getValue("reloj"), 0);
        equal(NV2.game.elapsed, 0); assert(api.running);
    });
    test("only resume is visible during pause; no state is lost", function () {
        var api = fakeAPI(); NV2.mount(api); NV2.dispatch("start"); api.setValue("reloj", 8);
        NV2.dispatch("pause");
        equal(NATURALES_UI.filter(function (name) { return api.visible[name]; }), ["resume"]);
        assert(!api.running); NV2.dispatch("answer", correct(NV2.game)); equal(NV2.game.teams[0].score, 0);
        NV2.dispatch("pause"); equal(NV2.game.elapsed, 8); assert(api.running);
    });
    test("correct option and explanation stay hidden during offer and selection", function () {
        var api = fakeAPI(); NV2.mount(api); NV2.dispatch("start");
        NV2.dispatch("answer", wrong(NV2.game)); NV2.dispatch("next");
        NV2.dispatch("help", "remove"); NV2.dispatch("answer", wrong(NV2.game));
        equal(NV2.game.phase, "offer"); equal(api.strings.explanation, ""); assert(!api.visible.explanation);
        equal(api.colors["answer" + correct(NV2.game)], [36, 43, 48]);
        NV2.dispatch("choose"); assert(api.visible.choose0); assert(!api.visible.choose1);
        NV2.dispatch("rescue", 0); equal(api.strings.explanation, "");
        NV2.dispatch("answer", correct(NV2.game)); assert(api.visible.explanation);
        assert(api.strings.explanation.length > 0);
    });
    test("unlimited games never start the native animation", function () {
        var api = fakeAPI(); NV2.mount(api); NV2.dispatch("seconds", -30); NV2.dispatch("start");
        assert(!api.running); assert(api.visible.helpTimeOff); assert(!api.visible.helpTime);
    });
    test("failure uses a pale background and success has its own color", function () {
        var api = fakeAPI(); NV2.mount(api); NV2.dispatch("start");
        NV2.dispatch("answer", wrong(NV2.game)); equal(api.backgrounds.status, "#F8E3E2");
        NV2.dispatch("next"); NV2.dispatch("answer", correct(NV2.game));
        equal(api.backgrounds.status, "#DEF0E4");
        equal(api.backgrounds["answer" + correct(NV2.game)], "#DAF0E1");
    });
    test("resting teams get a friendly message after an error or timeout", function () {
        var api = fakeAPI(); NV2.mount(api); NV2.dispatch("start");
        NV2.dispatch("answer", wrong(NV2.game));
        assert(api.strings.team0.indexOf("Descanso") !== -1);
        assert(api.strings.status.indexOf("pasa a descansar") !== -1);
        assert(api.strings.status.indexOf("eliminado") === -1);
        assert(api.strings.team0.indexOf("Fuera") === -1);
        NV2.dispatch("next"); api.setValue("reloj", 30);
        assert(api.strings.team1.indexOf("Descanso") !== -1);
        assert(api.strings.status.indexOf("pasa a descansar") !== -1);
        NV2.dispatch("choose"); NV2.dispatch("rescue", 0);
        NV2.dispatch("answer", correct(NV2.game));
        assert(api.strings.team0.indexOf("Descanso") === -1);
    });
    print("PASS: " + count + " tests");
})();
