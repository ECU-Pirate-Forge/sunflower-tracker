from controller import Robot

robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Initialize Hardware
motor = robot.getDevice('selector_motor')
sensor = robot.getDevice('switch_sensor')
sensor.enable(timestep)

keyboard = robot.getKeyboard()
keyboard.enable(timestep)

# Your specific X-axis positions
# (Make sure SliderJoint axis is 1 0 0 and minStop/maxStop are set!)
MODE_POSITIONS = [0.07, 0.06, 0.05] 
MODE_NAMES = ["Open", "Hybrid", "Closed"]

last_printed_mode = None
motor.setPosition(MODE_POSITIONS[0]) # Hold 'Open' immediately on start

while robot.step(timestep) != -1:
    key = keyboard.getKey()
    current_pos = sensor.getValue()

    # 1. Determine Target
    if key == ord('1'):
        target = MODE_POSITIONS[0]
        print("Manual override: Open (0.07)")
    elif key == ord('2'):
        target = MODE_POSITIONS[1]
        print("Manual override: Hybrid (0.06)")
    elif key == ord('3'):
        target = MODE_POSITIONS[2]
        print("Manual override: Closed (0.05)")
    else:
        # ONLY calculate 'closest' if no key is being pressed
        target = min(MODE_POSITIONS, key=lambda x: abs(x - current_pos))

    # 2. Set the position ONCE per loop
    motor.setPosition(target)

    # 3. Handle Printing
    mode_index = MODE_POSITIONS.index(target)
    current_mode_name = MODE_NAMES[mode_index]
    
    if current_mode_name != last_printed_mode:
        print(f"Current mode: {current_mode_name} | Position: {target}")
        last_printed_mode = current_mode_name