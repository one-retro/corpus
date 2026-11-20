// Drives a game for 1Retro's save tests. Reads Scripts\plan.json:
// { "steps": [ { "at": <frame>, "press": "A START ...", "hold": <frames> },
//              { "at": <frame>, "shot": "name" },
//              { "at": <frame>, "dump": [addr, len, "name"] },
//              { "at": <frame>, "quit": true } ] }
// A frame is one controller poll. Output goes to the folder plan.out names.
var BUTTONS = { A: 0x8000, B: 0x4000, Z: 0x2000, START: 0x1000, DU: 0x0800,
  DD: 0x0400, DL: 0x0200, DR: 0x0100, L: 0x0020, R: 0x0010, CU: 0x0008,
  CD: 0x0004, CL: 0x0002, CR: 0x0001 };
var STICK = { UP: [0, 80], DOWN: [0, -80], LEFT: [-80, 0], RIGHT: [80, 0] }; // also SX:<n> SY:<n>, -128..127
var dir = pj64.scriptsDirectory;
var plan = JSON.parse(fs.readfile(dir + "plan.json").toString());
var out = plan.out;
var frame = 0;
var held = []; // { until, buttons, x, y }
var log = [];
function note(s) { log.push(frame + ": " + s); fs.writefile(out + "log.txt", log.join("\n") + "\n"); }

function shot(name) {
  var status = mem.u32[0xA4400000];
  var origin = mem.u32[0xA4400004] & 0x00FFFFFF;
  var width = mem.u32[0xA4400008] & 0xFFF;
  var type = status & 3;
  if (type < 2 || width == 0) { note("shot " + name + ": no picture (status " + status.hex() + ")"); return; }
  var height = width > 320 ? 480 : 240;
  var bpp = type == 2 ? 2 : 4;
  var pixels = mem.getblock(0x80000000 + origin, width * height * bpp);
  var img = new N64Image(width, height, type == 2 ? IMG_RGBA16 : IMG_RGBA32, pixels);
  fs.writefile(out + name + ".png", img.toPNG());
  note("shot " + name + " " + width + "x" + height + " at " + origin.hex());
}

function run(step) {
  if (step.press) {
    var b = 0, x = 0, y = 0;
    step.press.split(" ").forEach(function (k) {
      if (BUTTONS[k] !== undefined) b |= BUTTONS[k];
      else if (STICK[k]) { x += STICK[k][0]; y += STICK[k][1]; }
      else if (k.indexOf("SX:") == 0) x = parseInt(k.substr(3), 10);
      else if (k.indexOf("SY:") == 0) y = parseInt(k.substr(3), 10);
    });
    held.push({ until: frame + (step.hold || 3), buttons: b, x: x, y: y });
    note("press " + step.press);
  }
  if (step.shot) shot(step.shot);
  if (step.dump) {
    fs.writefile(out + step.dump[2] + ".bin", mem.getblock(step.dump[0], step.dump[1]));
    note("dump " + step.dump[2]);
  }
  if (step.quit) { note("quit"); pj64.close(); }
}

events.onpifread(function () {
  frame++;
  if (frame == 1) note("first controller poll");
  plan.steps.forEach(function (s) {
    if (s.at != frame) return;
    try { run(s); } catch (e) { note("step failed: " + e); }
  });
  held = held.filter(function (h) { return h.until > frame; });
  var b = 0, x = 0, y = 0;
  held.forEach(function (h) { b |= h.buttons; if (h.x || h.y) { x = h.x; y = h.y; } });
  var ap = plan.autopilot;
  if (ap && frame >= ap.from && frame < ap.until) {
    // Steer toward a point a few path points ahead; the game state is read from RAM each poll.
    var px = mem.f32[ap.base + 0x14], pz = mem.f32[ap.base + 0x1C], yaw = mem.s16[ap.base + 0x2E];
    var n = ap.path.length, best = ap.idx || 0, bd = 1e18;
    for (var k = -3; k < 12; k++) {
      var j = ((best + k) % n + n) % n, dx = ap.path[j][0] - px, dz = ap.path[j][1] - pz;
      if (dx * dx + dz * dz < bd) { bd = dx * dx + dz * dz; ap.cand = j; }
    }
    ap.idx = ap.cand;
    var t = ap.path[(ap.idx + ap.look) % n];
    var want = Math.atan2(t[0] - px, t[1] - pz) * 32768 / Math.PI;
    var err = ((want - ap.sign * yaw + ap.offset) % 65536 + 65536 + 32768) % 65536 - 32768;
    x = Math.max(-80, Math.min(80, Math.round(err * ap.gain * ap.steer)));
    y = 0;
    ap.buttons.split(" ").forEach(function (k) { if (BUTTONS[k] !== undefined) b |= BUTTONS[k]; });
    if (ap.log && frame % ap.log == 0) note("ap pos " + px.toFixed(0) + "," + pz.toFixed(0) + " yaw " + yaw + " idx " + ap.idx + " err " + err.toFixed(0) + " x " + x);
    held.push({ until: frame + 1, buttons: 0, x: 0, y: 0 }); // make the write below happen
  }
  // Walk the PIF commands to find controller 1's read and write its answer.
  var i = 0, channel = 0;
  while (i < 63) {
    var tx = mem.u8[PIF_RAM_START + i];
    if (tx == 0xFE) break;
    if (tx == 0xFF) { i++; continue; }
    if (tx == 0) { channel++; i++; continue; }
    var rx = mem.u8[PIF_RAM_START + i + 1] & 0x3F;
    var cmd = mem.u8[PIF_RAM_START + i + 2];
    var at = PIF_RAM_START + i + 2 + tx;
    if (channel == 0 && cmd == 1 && rx == 4) {
      if (held.length) {
        mem.u8[at] = (b >> 8) & 0xFF; mem.u8[at + 1] = b & 0xFF;
        mem.u8[at + 2] = x & 0xFF; mem.u8[at + 3] = y & 0xFF;
      }
    }
    i += 2 + tx + rx;
    channel++;
  }
});
note("harness ready");
events.onstatechange(function (e) { note("state " + e.state); });
var ticks = 0;
setInterval(function () { ticks++; if (ticks % 5 == 0) note("tick " + ticks + " frames " + frame); }, 1000);
