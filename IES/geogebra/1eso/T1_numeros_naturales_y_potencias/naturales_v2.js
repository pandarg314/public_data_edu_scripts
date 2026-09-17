/* Embedded by generar_naturales_v2.py. ES5 for GeoGebra Classic 5 / Rhino. */
function NaturalesGame(bank, random) {
    this.bank = bank;
    this.random = random || Math.random;
    this.settings = {groups: 5, seconds: 30, extra: 20};
    this.phase = "setup";
    this.paused = false;
    this.confirmReset = false;
    this.teams = [];
    this.turn = 0;
    this.rescuer = -1;
    this.question = -1;
    this.pending = [];
    this.excluded = [];
    this.eligible = [];
    this.elapsed = 0;
    this.limit = 0;
    this.round = 0;
    this.clockId = 0;
    this.message = "";
    this.tone = "neutral";
}

NaturalesGame.prototype.running = function () {
    return !this.paused && !this.confirmReset &&
        (this.phase === "active" || this.phase === "rescue");
};
NaturalesGame.prototype.actor = function () {
    return this.rescuer >= 0 ? this.rescuer : this.turn;
};
NaturalesGame.prototype.living = function () {
    var result = [];
    for (var i = 0; i < this.teams.length; i++) {
        if (this.teams[i].alive) result.push(i);
    }
    return result;
};
NaturalesGame.prototype.start = function () {
    if (this.phase !== "setup" || this.paused || !this.bank.length) return;
    this.teams = [];
    for (var i = 0; i < this.settings.groups; i++) {
        this.teams.push({alive: true, score: 0, pass: true, time: true,
            remove: true, revive: true});
    }
    this.turn = 0;
    this.round = 0;
    this.pending = [];
    this.draw();
};
NaturalesGame.prototype.draw = function () {
    if (!this.pending.length) {
        for (var i = 0; i < this.bank.length; i++) this.pending.push(i);
    }
    var pos = Math.floor(this.random() * this.pending.length);
    this.question = this.pending.splice(pos, 1)[0];
    this.excluded = [];
    this.eligible = [];
    this.rescuer = -1;
    this.elapsed = 0;
    this.limit = this.settings.seconds;
    this.clockId++;
    this.round++;
    this.message = "";
    this.tone = "neutral";
    this.phase = "active";
};
NaturalesGame.prototype.tick = function (seconds) {
    if (!this.running() || this.limit === 0 || !isFinite(seconds)) return;
    this.elapsed = Math.max(this.elapsed, seconds);
    if (this.elapsed >= this.limit - 0.000001) {
        this.elapsed = this.limit;
        this.fail(-1);
    }
};
NaturalesGame.prototype.answer = function (option) {
    if (!this.running() || option < 0 || option > 3 || option % 1 ||
            this.excluded.indexOf(option) !== -1) return;
    if (option !== this.bank[this.question].correct) {
        this.fail(option);
        return;
    }
    var actor = this.actor();
    var team = this.teams[actor];
    team.score++;
    if (this.phase === "rescue") {
        team.alive = true;
        team.pass = team.time = team.remove = false;
        this.message = "Grupo " + (actor + 1) + " vuelve al juego. +1 punto";
    } else {
        this.message = "Grupo " + (actor + 1) + ": correcto. +1 punto";
    }
    this.phase = "closed";
    this.tone = "success";
};
NaturalesGame.prototype.fail = function (option) {
    if (!this.running()) return;
    var actor = this.actor();
    if (option >= 0) this.excluded.push(option);
    this.teams[actor].alive = false;
    this.message = (option < 0 ? "Tiempo agotado. " : "Esta vez no. ") +
        "El Grupo " + (actor + 1) + " pasa a descansar.";
    this.tone = "failure";
    if (this.phase === "rescue") {
        this.phase = "closed";
        return;
    }
    this.eligible = [];
    for (var i = 0; i < this.teams.length; i++) {
        if (i !== actor && !this.teams[i].alive && this.teams[i].revive) {
            this.eligible.push(i);
        }
    }
    this.phase = this.eligible.length ? "offer" : "closed";
};
NaturalesGame.prototype.help = function (kind) {
    if (this.phase !== "active" || !this.running()) return;
    var team = this.teams[this.turn];
    if (["pass", "time", "remove"].indexOf(kind) === -1 || !team[kind]) return;
    if (kind === "time" && this.limit === 0) return;
    team[kind] = false;
    if (kind === "pass") {
        this.advance();
    } else if (kind === "time") {
        this.limit += this.settings.extra;
    } else {
        var choices = [];
        for (var i = 0; i < 4; i++) {
            if (i !== this.bank[this.question].correct &&
                    this.excluded.indexOf(i) === -1) choices.push(i);
        }
        this.excluded.push(choices[Math.floor(this.random() * choices.length)]);
    }
};
NaturalesGame.prototype.advance = function () {
    var alive = this.living();
    if (alive.length <= 1) {
        this.phase = "over";
        this.message = alive.length ? "Gana el Grupo " + (alive[0] + 1) :
            "Fin de partida: no quedan equipos activos.";
        this.tone = alive.length ? "success" : "neutral";
        return;
    }
    for (var step = 1; step <= this.teams.length; step++) {
        var next = (this.turn + step) % this.teams.length;
        if (this.teams[next].alive) {
            this.turn = next;
            this.draw();
            return;
        }
    }
};
NaturalesGame.prototype.dispatch = function (action, value) {
    if (this.confirmReset) {
        if (action === "cancelReset") this.confirmReset = false;
        if (action === "reset") {
            this.confirmReset = false;
            this.phase = "setup";
            this.paused = false;
            this.elapsed = 0;
            this.clockId++;
        }
        return;
    }
    if (action === "pause" && this.phase !== "setup") {
        this.paused = !this.paused;
        return;
    }
    if (this.paused) return;
    if (action === "requestReset" && this.phase !== "setup") {
        this.confirmReset = true;
        return;
    }
    if (this.phase === "setup") {
        if (action === "start") this.start();
        if (action === "groups") this.settings.groups = Math.max(2, Math.min(8, this.settings.groups + value));
        if (action === "seconds") this.settings.seconds = Math.max(0, Math.min(120, this.settings.seconds + value));
        if (action === "extra") this.settings.extra = Math.max(5, Math.min(120, this.settings.extra + value));
        return;
    }
    if (action === "answer") this.answer(value);
    if (action === "help") this.help(value);
    if (action === "choose" && this.phase === "offer") this.phase = "choosing";
    else if (action === "choose" && this.phase === "choosing") this.phase = "offer";
    if (action === "rescue" && this.phase === "choosing" && this.eligible.indexOf(value) !== -1) {
        this.rescuer = value;
        this.teams[value].revive = false;
        this.elapsed = 0;
        this.limit = this.settings.seconds;
        this.clockId++;
        this.phase = "rescue";
        this.message = "Oportunidad de revivir: Grupo " + (value + 1);
        this.tone = "neutral";
    }
    if (action === "reveal" && (this.phase === "offer" || this.phase === "choosing")) {
        this.phase = "closed";
    }
    if (action === "next" && this.phase === "closed") this.advance();
};

var NV2 = {
    game: null, api: null, busy: false, cache: {}, clockId: -1,
    mount: function (api) {
        this.api = api;
        this.game = new NaturalesGame(NATURALES_BANK);
        this.cache = {};
        this.clockId = -1;
        this.busy = true;
        api.setAnimating("reloj", false);
        api.setValue("reloj", 0);
        api.registerObjectUpdateListener("reloj", "naturalesClock");
        this.render();
        this.busy = false;
    },
    clock: function () {
        if (this.busy || !this.game) return;
        this.busy = true;
        try {
            this.game.tick(Number(this.api.getValue("reloj")));
            this.render();
        } finally { this.busy = false; }
    },
    dispatch: function (action, value) {
        if (this.busy || !this.game) return;
        this.busy = true;
        try {
            // Check the deadline before any click, even between animation frames.
            this.game.tick(Number(this.api.getValue("reloj")));
            this.game.dispatch(action, value);
            this.render();
        } finally { this.busy = false; }
    },
    set: function (method, name, value) {
        var key = method + ":" + name;
        if (this.cache[key] === value) return;
        this.cache[key] = value;
        this.api[method](name, value);
    },
    color: function (name, color) {
        if (this.cache["color:" + name] === color.join(",")) return;
        this.cache["color:" + name] = color.join(",");
        this.api.setColor(name, color[0], color[1], color[2]);
    },
    background: function (name, color) {
        if (this.cache["background:" + name] === color.join(",")) return;
        // This command accepts 0..1 components, unlike the API's setColor (0..255).
        var hex = "#" + color.map(function (part) {
            return ("0" + part.toString(16)).slice(-2);
        }).join("").toUpperCase();
        if (this.api.evalCommand('SetBackgroundColor(' + name + ', "' + hex + '")')) {
            this.cache["background:" + name] = color.join(",");
        }
    },
    render: function () {
        var self = this, g = this.game, visible = {};
        function show(name) { visible[name] = true; }
        function text(name, value) { show(name); self.set("setTextValue", name, value); }
        function icon(name, enabled) { show(name + (enabled ? "" : "Off")); }
        var hide = g.paused || g.confirmReset;
        this.api.setRepaintingActive(false);
        try {
            if (g.paused) {
                show("resume");
            } else if (g.confirmReset) {
                text("resetTitle", "Nueva partida");
                text("resetQuestion", "Se reiniciar\u00e1n los puntos y los comodines.");
                show("resetYes"); show("resetNo");
            } else {
                show("title");
                if (g.phase === "setup") {
                    text("configGroups", "Equipos: " + g.settings.groups);
                    text("configTime", "Tiempo por reto: " + (g.settings.seconds ? g.settings.seconds + " s" : "sin l\u00edmite"));
                    text("configExtra", "Comod\u00edn de tiempo: +" + g.settings.extra + " s");
                    ["groupsMinus", "groupsPlus", "timeMinus", "timePlus", "extraMinus", "extraPlus", "start"].forEach(show);
                } else {
                    show("pause"); show("restart");
                    text("round", "Reto " + g.round + "  |  " + g.pending.length + " pendientes");
                    var q = this.game.bank[g.question];
                    var reveal = g.phase === "closed" || g.phase === "over";
                    text("topic", q.topic);
                    text("question", q.question);
                    text("expression", q.expression);
                    for (var i = 0; i < 4; i++) {
                        var excluded = g.excluded.indexOf(i) !== -1;
                        text("answer" + i, "\\;\\text{" + "ABCD".charAt(i) + ")}\\quad " + q.options[i] + "\\;");
                        this.color("answer" + i, reveal && i === q.correct ? [25, 110, 79] : excluded ? [140, 145, 148] : [36, 43, 48]);
                        this.background("answer" + i, reveal && i === q.correct ? [218, 240, 225] : excluded ? [236, 237, 238] : [238, 244, 246]);
                    }
                    // Do not leave the solution in an invisible text object during a rebound.
                    this.set("setTextValue", "explanation", reveal ? q.explanation : "");
                    if (reveal) show("explanation");
                    if (g.message) text("status", " " + g.message + " ");
                    this.background("status", g.tone === "failure" ? [248, 227, 226] : g.tone === "success" ? [222, 240, 228] : [239, 242, 243]);
                    this.color("status", g.tone === "failure" ? [128, 61, 64] : [33, 90, 72]);
                    text("turn", g.phase === "over" ? "Partida finalizada" :
                        (g.phase === "rescue" ? "Revive: Grupo " : "Turno: Grupo ") + (g.actor() + 1));
                    text("clock", g.limit ? Math.max(0, Math.ceil(g.limit - g.elapsed - 0.000001)) + " s" : "Sin l\u00edmite");
                    if (g.phase === "active" || g.phase === "rescue") {
                        var team = g.teams[g.actor()];
                        var normal = g.phase === "active";
                        icon("helpPass", normal && team.pass);
                        icon("helpTime", normal && team.time && g.limit > 0);
                        icon("helpRemove", normal && team.remove);
                        text("extraAmount", "+" + g.settings.extra + " s");
                        this.color("extraAmount", normal && team.time && g.limit > 0 ? [42, 91, 100] : [139, 147, 152]);
                    }
                    if (g.phase === "offer" || g.phase === "choosing") {
                        show("addTeam"); show("reveal");
                        text("rescueTitle", "Oportunidad de revivir");
                    }
                    if (g.phase === "closed") show("next");
                    for (var k = 0; k < g.teams.length; k++) {
                        var t = g.teams[k];
                        var current = g.phase !== "over" && g.actor() === k;
                        text("team" + k, "Grupo " + (k + 1) + "   " + t.score + (t.score === 1 ? " punto" : " puntos") + (t.alive ? "" : "   Descanso"));
                        this.color("team" + k, t.alive ? [34, 46, 48] : [133, 136, 140]);
                        this.background("team" + k, current ? [232, 238, 215] : [250, 251, 252]);
                        ["pass", "time", "remove", "revive"].forEach(function (kind) {
                            icon("team" + k + "_" + kind, t[kind] && (kind === "revive" || t.alive));
                        });
                        if (g.phase === "choosing" && g.eligible.indexOf(k) !== -1) show("choose" + k);
                    }
                }
            }
            for (var j = 0; j < NATURALES_UI.length; j++) {
                this.set("setVisible", NATURALES_UI[j], !!visible[NATURALES_UI[j]]);
            }
            if (this.clockId !== g.clockId) {
                this.api.setAnimating("reloj", false);
                this.api.setValue("reloj", 0);
                this.clockId = g.clockId;
                this.cache.animating = false;
            }
            var animate = !hide && g.running() && g.limit > 0;
            if (this.cache.animating !== animate) {
                this.api.setAnimating("reloj", animate);
                if (animate) this.api.startAnimation();
                else this.api.stopAnimation();
                this.cache.animating = animate;
            }
        } finally { this.api.setRepaintingActive(true); }
    }
};

function naturalesClock() { NV2.clock(); }
function ggbOnInit() { NV2.mount(ggbApplet); }
