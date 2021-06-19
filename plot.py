import calculation
from bokeh.layouts import column, row, Spacer
from bokeh.models import CustomJS, Slider, Div, Panel, Tabs
from bokeh.plotting import ColumnDataSource, figure


def veh_env_reg(color, source, start_time_frame_slider, end_time_frame_slider,
                start_velocity, end_velocity, angle, mass, engine_torque,
                wheels_radius, wind, aerodynamic_drag):
    start_velocity_slider = Slider(start=0, end=200, value=start_velocity, step=1,
                                   title="Start Velocity (km/h)", bar_color=color)
    end_velocity_slider = Slider(start=0, end=200, value=end_velocity, step=1,
                                 title="End Velocity (km/h)", bar_color=color)
    angle_slider = Slider(start=0, end=20, value=angle, step=0.1,
                          title="Angle (degrees)", bar_color=color)
    mass_slider = Slider(start=1500, end=3000, value=mass, step=10,
                         title="Mass of the Car (kg)", bar_color=color)
    engine_torque_slider = Slider(start=100, end=3000, value=engine_torque, step=10,
                                  title="Engine Torque (Nm)", bar_color=color)
    wheels_radius_slider = Slider(start=0.1, end=.5, value=wheels_radius, step=0.01,
                                  title="Wheels radius (m)", bar_color=color)
    wind_slider = Slider(start=-100, end=100, value=wind, step=1,
                         title="Wind speed (km/h, >0 same as direction of travel)", bar_color=color)
    aerodynamic_drag_slider = Slider(start=0, end=1, value=aerodynamic_drag, step=0.01,
                                     title="Aerodynamic drag", bar_color=color)
    k_p_slider = Slider(start=-2, end=2, value=0, step=.1,
                        title="Kp (10^X)", bar_color=color)
    t_p_slider = Slider(start=-3, end=1, value=-2, step=.1,
                        title="Tp (10^X)", bar_color=color)
    t_i_slider = Slider(start=-3, end=3, value=-1, step=.1,
                        title="Ti (10^X)", bar_color=color)

    veh_params = [start_velocity_slider, end_velocity_slider, mass_slider, engine_torque_slider,
                  wheels_radius_slider, aerodynamic_drag_slider]
    env_params = [angle_slider, wind_slider]
    reg_params = [k_p_slider, t_p_slider, t_i_slider]

    callback = CustomJS(args=dict(source=source, start_velocity=start_velocity_slider,
                                  end_velocity=end_velocity_slider, ang=angle_slider, mass=mass_slider,
                                  torque=engine_torque_slider, wheels=wheels_radius_slider, wind=wind_slider,
                                  aerodynamic_drag=aerodynamic_drag_slider,
                                  stf=start_time_frame_slider, etf=end_time_frame_slider,
                                  t_p=t_p_slider, t_i=t_i_slider, k_p=k_p_slider), code=open("callback.js").read())

    for s in veh_params:
        s.js_on_change('value', callback)
    for s in env_params:
        s.js_on_change('value', callback)
    for s in reg_params:
        s.js_on_change('value', callback)

    return veh_params, env_params, reg_params, callback


def sim(start_velocity=0, end_velocity=10, angle=0, mass=1500, engine_torque=400,
        wheels_radius=0.41, wind=0, aerodynamic_drag=0.25, duration=200):
    init_data = calculation.calculate(start_velocity / 3.6, end_velocity / 3.6, angle, mass, engine_torque,
                                      wheels_radius, wind, aerodynamic_drag, duration)

    max_duration = 2000
    start_time_frame_slider = Slider(start=0, end=max_duration - 20, value=0, step=20, title="Start Time Frame")
    end_time_frame_slider = Slider(start=20, end=max_duration, value=200, step=20, title="End Time Frame")
    sim_params = [start_time_frame_slider, end_time_frame_slider]
    return sim_params, init_data[0], init_data[1], init_data[2]


def make_plot(start_velocity=0, end_velocity=10, angle=0, mass=1500, engine_torque=400,
              wheels_radius=0.3, wind=0, aerodynamic_drag=0.25, duration=200):
    sim_params, t_all, v_all, a_all = sim(start_velocity, end_velocity, angle, mass, engine_torque,
                                          wheels_radius, wind, aerodynamic_drag, duration)
    source = ColumnDataSource(data=dict(t_all=t_all, v_all=v_all, a_all=a_all))

    plot_v = figure(
        tools="pan,wheel_zoom,box_zoom,reset,save",
        x_axis_label="t [s]",
        y_axis_label="v [km/h]",
        plot_width=800,
        plot_height=800)

    plot_a = figure(
        tools="pan,wheel_zoom,box_zoom,reset,save",
        x_axis_label="t [s]",
        y_axis_label="a [m/s^2]",
        plot_width=800,
        plot_height=800)

    plot_v.line(x='t_all', y='v_all', source=source, line_color="#29A337", line_width=2)
    plot_a.line(x='t_all', y='a_all', source=source, line_color="#29A337", line_width=2)

    tab1 = Panel(child=plot_v, title="Velocity")
    tab2 = Panel(child=plot_a, title="Acceleration")

    veh_params, env_params, reg_params, callback = veh_env_reg("#29A337", source,
                                                               sim_params[0], sim_params[1],
                                                               start_velocity, end_velocity,
                                                               angle, mass, engine_torque,
                                                               wheels_radius, wind, aerodynamic_drag)

    for s in sim_params:
        s.js_on_change("value", callback)

    return row(Tabs(tabs=[tab1, tab2]), Spacer(width=50),
               column(Div(text="<h3>Vehicle parameters</h3>"),
                      column(veh_params),
                      Div(text="<h3>Environment parameters</h3>"),
                      column(env_params),
                      Div(text="<h3>Regulator parameters</h3>"),
                      column(reg_params)), Spacer(width=50),
               column(Div(text="<h3>Simulation parameters</h3>"),
                      column(sim_params)))


def make_plots(start_velocity=0, end_velocity=10, angle=0, mass=1500, engine_torque=400,
               wheels_radius=0.3, wind=0, aerodynamic_drag=0.25, duration=200):
    sim_params, t_all, v_all, a_all = sim(start_velocity, end_velocity, angle, mass, engine_torque,
                                          wheels_radius, wind, aerodynamic_drag, duration)

    b_t_all = t_all
    r_t_all = t_all
    b_v_all = v_all
    r_v_all = v_all
    b_a_all = a_all
    r_a_all = a_all
    b_source = ColumnDataSource(data=dict(t_all=b_t_all, v_all=b_v_all, a_all=b_a_all))
    r_source = ColumnDataSource(data=dict(t_all=r_t_all, v_all=r_v_all, a_all=r_a_all))

    plot_v = figure(
        tools="pan,box_zoom,wheel_zoom,reset,save",
        x_axis_label="t [s]",
        y_axis_label="v [km/h]",
        plot_width=800,
        plot_height=800)

    plot_a = figure(
        tools="pan,box_zoom,wheel_zoom,reset,save",
        x_axis_label="t [s]",
        y_axis_label="a [m/s^2]",
        plot_width=800,
        plot_height=800)

    plot_v.line(x='t_all', y='v_all', source=b_source, line_color='#4377B1', line_width=2)
    plot_v.line(x='t_all', y='v_all', source=r_source, line_color='#FB4D3D', line_width=2)
    plot_a.line(x='t_all', y='a_all', source=b_source, line_color='#4377B1', line_width=2)
    plot_a.line(x='t_all', y='a_all', source=r_source, line_color='#FB4D3D', line_width=2)
    tab1 = Panel(child=plot_v, title="Velocity")
    tab2 = Panel(child=plot_a, title="Acceleration")

    b_veh_params, b_env_params, b_reg_params, b_callback = veh_env_reg("#4377B1", b_source,
                                                                       sim_params[0], sim_params[1],
                                                                       start_velocity, end_velocity,
                                                                       angle, mass, engine_torque,
                                                                       wheels_radius, wind, aerodynamic_drag)
    r_veh_params, r_env_params, r_reg_params, r_callback = veh_env_reg("#FB4D3D", r_source,
                                                                       sim_params[0], sim_params[1],
                                                                       start_velocity, end_velocity,
                                                                       angle, mass, engine_torque,
                                                                       wheels_radius, wind, aerodynamic_drag)

    for s in sim_params:
        s.js_on_change("value", b_callback, r_callback)

    return row(Tabs(tabs=[tab1, tab2]), Spacer(width=50),
               column(Div(text="<h3>Vehicle parameters</h3>"),
                      column(b_veh_params),
                      Div(text="<h3>Environment parameters</h3>"),
                      column(b_env_params),
                      Div(text="<h3>Regulator parameters</h3>"),
                      column(b_reg_params)), Spacer(width=50),
               column(Div(text="<h3>Vehicle parameters</h3>"),
                      column(r_veh_params),
                      Div(text="<h3>Environment parameters</h3>"),
                      column(r_env_params),
                      Div(text="<h3>Regulator parameters</h3>"),
                      column(r_reg_params)), Spacer(width=50),
               column(Div(text="<h3>Simulation parameters</h3>"),
                      column(sim_params)))
