def frame_sampling(frames) -> list:
    """Return sampled frames from initial set of frames by dropping frames."""
    count = 0
    sampled_frames = []
    for i in frames:
        if count == 4:  # Take only every (Settings.sampling_ratio + 1) frame.
            count = 0
            sampled_frames.append(i)
            # print(i)
        else:
            count += 1

    return sampled_frames


o = frame_sampling(range(200))
print(len(o))
