const data = source.data;
const t_all = data['t_all'];
const v_all = data['v_all'];
const a_all = data['a_all'];
const M = mass.value;                                             // mass of the car
const Tor = torque.value;                                         // engine torque
const r = wheels.value;                                           // radius of wheels
const Ca = aerodynamic_drag.value;                                // aerodynamic drag coefficient
const Fd = [-Tor/r, Tor/r];                                       // range of engine force
const v = [start_velocity.value / 3.6, end_velocity.value / 3.6]; // range of velocity for car
const v_w = wind.value;                                           // wind velocity (>0 opposite to driving direction)
const angle = angle_verify();                                     // road slope in radians

const T = {'i':Math.pow(10, t_i.value), 'p':Math.pow(10, t_p.value)};
const N_start = stf.value / T['p'];
const N = etf_verify() / T['p'];

let vs = [v[0]];
t_all.length = 0;
v_all.length = 0;
a_all.length = 0;
if (stf.value === 0) {
    v_all.push(v[0] * 3.6);
    t_all.push(0);
    a_all.push(0);
}
let e = [0.0, 0.0];
let de = [0.0, 0.0];
let u = [-2, 2];
let u_curr = 0.0;
const kp = Math.pow(10, k_p.value);

function etf_verify() {
    if (etf.value - stf.value < 20)
        etf.value = stf.value + 20;
    return etf.value;
}

function angle_verify() {
    let max_val = clamp(Math.asin((Fd[1] - fa_calc(end_velocity.value)) / (M * 9.81)) * 180 / Math.PI, 0, 20);
    if (isNaN(max_val))
        max_val = 0;
    if(Fd[1] <= M * 9.81 * Math.sin(ang.value * Math.PI / 180) + fa_calc(end_velocity.value))
        ang.value = max_val;
    ang.end = max_val;
    ang.title = "Angle (degrees, max=" + Math.round(max_val * 100) / 100 + ")";
    return ang.value * Math.PI / 180;
}

function clamp(val, mn, mx) {
    if(val < mn)
        return mn;
    if(val > mx)
        return mx;
    return val;
}

function e_calc(v_curr) {
    e[0] = e[1];
    e[1] = v[1] - v_curr;
    de[0] = de[1];
    de[1] = e[1] - e[0];
}

function du_calc() { return kp * (de[1] + (T['p'] / T['i']) * e[1]); }

function fg_calc() { return M * 9.81 * Math.sin(angle); }

function fa_calc(v_curr) {
    return Math.sign(v_curr - v_w) * Ca * (v_curr - v_w) ** 2;
}

function fd_calc() {
    u_curr = clamp(u_curr, u[0], u[1]);
    return (u_curr * (Fd[1] - Fd[0])) / (u[1] - u[0]);
}

function v_calc(v_num) {
    let v_curr = vs[v_num - 1];
    e_calc(v_curr);
    u_curr += du_calc();
    return ((fd_calc() - (fg_calc() + fa_calc(v_curr))) / M) * T['p'] + v_curr;
}

for (let i = 1; i < N; i++) {
    let v_ = v_calc(i);
    vs.push(v_);
    if (i >= N_start) {
        t_all.push(i * T['p']);
        v_all.push(v_ * 3.6);
        a_all.push((vs[i] - vs[i - 1]) / T['p']);
    }
}
source.change.emit();