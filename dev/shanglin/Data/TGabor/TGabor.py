from psychopy import visual, event, core, sound 
import sys
import numpy as np
import random
import pandas as pd
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib

def runTG(session, pid, n_practices, n_trials):

    correctSound1 = sound.Sound(value=600, secs=0.1)
    correctSound2 = sound.Sound(value=800, secs=0.1)
    errorSound = sound.Sound(value=500, secs=0.2)

    trialClock = core.Clock()

    # Parameters
    oris = ['left', 'right']
    soa1 = 12
    soa2 = 12
    soa_practice = [12, 14, 16]
    step_size = 1
    correct_counter1 = 0
    correct_counter2 = 0
    data = []
    
    # Default starting parameter flag
    csv_path = f"E:/data6/ind-spacevtime/TGabor/Data/{pid}_TGabor.csv"

    # Load existing CSV if session > 0
    if session > 0:
        data = pd.read_csv(csv_path)
        if session > 1:
        # Load contrast value from last session
            with open(csv_path, 'r') as f:
                last_line = f.readlines()[-1]
                soa1 = int(last_line.strip().split(',')[-2])
                soa2 = int(last_line.strip().split(',')[-1])
                
    # If session 0, initialize CSV with header only (no data)
    if session == 0:
        data = pd.DataFrame(columns=["session", "trial","staircase", "orientation", "response", "correct", "soa1", "soa2"])
        data.to_csv(csv_path, index=False)


    FixationFrame = 80
    NosieFrame = 8
    
    # Gabor stimulus functions
    def GaborImage(ori, contrast=0.05, size=512, sf=5, decay=0.25):
        x = np.linspace(-1, 1, size)
        y = np.linspace(-1, 1, size)
        X, Y = np.meshgrid(x, y)

        theta = np.deg2rad(-45) if ori == 'left' else np.deg2rad(45)
        X_rot = X * np.cos(theta) + Y * np.sin(theta)
        phase = np.random.uniform(0, 2 * np.pi)
        grating = contrast * np.cos(2 * np.pi * sf * X_rot + phase)
        gauss = np.exp(-(X**2 + Y**2) / (2 * decay**2))
        gabor = grating * gauss
        return np.clip(gabor, -1, 1)

    def GaborMask(size=512, noise_mean=0.0, noise_std=0.4):
        squeeze_size = size // 8
        squeeze_noise = np.random.normal(loc=noise_mean, scale=noise_std, size=(squeeze_size, squeeze_size))
        noise = np.repeat(np.repeat(squeeze_noise, 8, axis=0), 8, axis=1)
        return np.clip(noise, -1, 1)

    # Visual Setup
    win = visual.Window(size=(1920, 1200), color=0, units="pix", fullscr=True)
    stim = visual.ImageStim(win, size=(512, 512), units="pix")

    # Welcome Screen
    text = visual.TextStim(win, text="Welcome to the experiment! \n Press the SPACE key to begin the instruction", font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=2000,units="pix")
    text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    # Instruction Screen
    text = visual.TextStim(win, text="In this experiment, you will see a grating followed by visual noise. \n The grating will either point up and to the RIGHT, or up and to the LEFT.\
    \n\nThe example below points up and to the LEFT.\
    \n\nPress the 'x' key if you think the grating is pointing up and to the LEFT. \n Press the 'm' key if you think the grating is pointing up and to the RIGHT.\
    \n\nWhen you are done reviewing the instructions, press the SPACE key to continue.", font="Dejavusans-bold", color=1.0, height=24, pos=(0,300), wrapWidth=2000,units="pix")
    text.draw()
    image = visual.ImageStim(image=np.flipud(GaborImage(ori='left', contrast=0.25)), win=win, size=(512, 512), pos=(0, -250), units="pix")
    image.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    if session == 0:
        # Practice trials with feedback
        text = visual.TextStim(win, text="You will now be given several practice trials. \n You will be given feedback after each trial.\n\nPress SPACE to begin the practice trials.", font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=2000,units="pix")
        text.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

        for trial in range(n_practices):
            if 'escape' in event.getKeys():
                print("Experiment aborted by user.")
                break

            fixation = visual.TextStim(win, text="+", color=1.0, height=48)
            ori = random.choice(oris)
            practice_soa = random.choice(soa_practice)
            stim.image = np.flipud(GaborImage(ori=ori))

            noise_frames = [visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(GaborMask())) for _ in range(5)]

            frames = [fixation, stim] + noise_frames
            frameDurations = [FixationFrame, practice_soa] + [NosieFrame]*5
            exlib.runFrames(win, frames, frameDurations, trialClock)

            wait = visual.TextStim(win, text="", color=1.0, height=48)
            wait.draw()
            win.flip()
            keys = event.getKeys(keyList=['x', 'm', 'escape'])
            if not keys:
                keys = event.waitKeys(keyList=['x', 'm', 'escape'])
            if 'escape' in keys:
                print("Experiment aborted by user.")
                break

            response = 'left' if keys[0] == 'x' else 'right'
            correct = response == ori

            if correct:
                feedback = visual.TextStim(win, text="Correct!", color='green', height=36)
                feedback.draw()
                win.flip()
                correctSound1.play()
                core.wait(0.1)
                correctSound2.play()
                core.wait(0.4)
            else:
                feedback = visual.TextStim(win, text="Wrong!", color='red', height=36)
                feedback.draw()
                win.flip()
                errorSound.play()
                core.wait(0.5)

            win.flip()
            core.wait(0.5)

    else:
        # Main experiment block
        text = visual.TextStim(win, text=f"Main Experiment (Session {session})\n\nPress the SPACE key to begin the trial block.", font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=2000,units="pix")
        text.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

        for trial in range(round(n_trials/2)):
            if 'escape' in event.getKeys():
                print("Experiment aborted by user.")
                break

            # 2D1U
            fixation = visual.TextStim(win, text="+", color=1.0, height=48)
            ori = random.choice(oris)
            stim.image = np.flipud(GaborImage(ori=ori))

            noise_frames = [visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(GaborMask())) for _ in range(5)]

            frames = [fixation, stim] + noise_frames
            frameDurations = [FixationFrame, soa1] + [NosieFrame]*5
            
            exlib.runFrames(win, frames, frameDurations, trialClock)

            wait = visual.TextStim(win, text="", color=1.0, height=48)
            wait.draw()
            win.flip()
            keys = event.getKeys(keyList=['x', 'm', 'escape'])
            if not keys:
                keys = event.waitKeys(keyList=['x', 'm', 'escape'])
            if 'escape' in keys:
                print("Experiment aborted by user.")
                break
            win.flip()

            response = 'left' if keys[0] == 'x' else 'right'
            correct = response == ori

            if correct:
                correctSound1.play()
                core.wait(0.1)
                correctSound2.play()
                core.wait(0.4)
            else:
                errorSound.play()
                core.wait(0.5)

            data.loc[len(data)] = {
                "session": session,
                "trial": trial + 1,
                "staircase": 2,
                "orientation": ori,
                "response": response,
                "correct": correct,
                "soa1": round(soa1),
                "soa2": round(soa2)
                }

            if correct:
                correct_counter1 += 1
                if correct_counter1 == 2:
                    soa1 = max(0, soa1 - step_size)
                    correct_counter1 = 0
            else:
                soa1 = soa1 + step_size
                correct_counter1 = 0
            core.wait(0.5)


            # 3D1U
            fixation = visual.TextStim(win, text="+", color=1.0, height=48)
            ori = random.choice(oris)
            stim.image = np.flipud(GaborImage(ori=ori))

            noise_frames = [visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(GaborMask())) for _ in range(5)]

            frames = [fixation, stim] + noise_frames
            frameDurations = [FixationFrame, soa2] + [NosieFrame]*5
            
            exlib.runFrames(win, frames, frameDurations, trialClock)

            wait = visual.TextStim(win, text="", color=1.0, height=48)
            wait.draw()
            win.flip()
            keys = event.getKeys(keyList=['x', 'm', 'escape'])
            if not keys:
                keys = event.waitKeys(keyList=['x', 'm', 'escape'])
            if 'escape' in keys:
                print("Experiment aborted by user.")
                break
            win.flip()

            response = 'left' if keys[0] == 'x' else 'right'
            correct = response == ori

            if correct:
                correctSound1.play()
                core.wait(0.1)
                correctSound2.play()
                core.wait(0.4)
            else:
                errorSound.play()
                core.wait(0.5)

            data.loc[len(data)] = {
                "session": session,
                "trial": trial + 1,
                "staircase": 3,
                "orientation": ori,
                "response": response,
                "correct": correct,
                "soa1": round(soa1),
                "soa2": round(soa2)
                }

            if correct:
                correct_counter2 += 1
                if correct_counter2 == 3:
                    soa2 = max(0, soa2 - step_size)
                    correct_counter2 = 0
            else:
                soa2 = soa2 + step_size
                correct_counter2 = 0
            core.wait(0.5)

    # Save data with session as first column
    win.close()
    
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)