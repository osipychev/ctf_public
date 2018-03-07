from gym.envs.registration import register


register(
    id='cap-v0',
    entry_point='gym_cap.envs:CapEnvGenerate20x20',
)

register(
    id='cap-v1',
    entry_point='gym_cap.envs:CapEnvGenerate100x100',
)

register(
    id='cap-v2',
    entry_point='gym_cap.envs:CapEnvGenerate500x500',
)