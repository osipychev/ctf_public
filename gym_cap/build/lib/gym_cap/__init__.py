from gym.envs.registration import register


register(
    id='capRandom-v0',
    entry_point='gym_cap.envs:CapEnvGenerate20x20Random',
)
register(
    id='capRandom-v1',
    entry_point='gym_cap.envs:CapEnvGenerate100x100Random',
)

register(
    id='capRandom-v2',
    entry_point='gym_cap.envs:CapEnvGenerate500x500Random',
)

register(
    id='capHuman-v0',
    entry_point='gym_cap.envs:CapEnvGenerate20x20Human',
)

register(
    id='capHuman-v1',
    entry_point='gym_cap.envs:CapEnvGenerate100x100Human',
)

register(
    id='capHuman-v2',
    entry_point='gym_cap.envs:CapEnvGenerate500x500Human',
)

register(
    id='capSandbox-v0',
    entry_point='gym_cap.envs:CapEnvGenerate20x20Sandbox',
)

register(
    id='capSandbox-v1',
    entry_point='gym_cap.envs:CapEnvGenerate100x100Sandbox',
)

register(
    id='capSandbox-v2',
    entry_point='gym_cap.envs:CapEnvGenerate500x500Sandbox',
)

