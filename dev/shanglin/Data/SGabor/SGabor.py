from psychopy import visual, event, core, sound
import sys
import numpy as np
import random
import pandas as pd
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib

def runSG(session, pid, n_practices, n_trials):
    
    correctSound1 = sound.Sound(value=600, secs=0.1)
    correctSound2 = sound.Sound(value=800, secs=0.1)
    errorSound = sound.Sound(value=500, secs=0.2)

    trialClock = core.Clock()
    
    # Parameters
    oris = ['left', 'right']
    contrast1 = 0.6
    contrast2 = 0.6
    contrast_practice = [0.6, 0.7, 0.8]
    step_size = 0.05
    correct_counter1 = 0
    correct_counter2 = 0
    data = []

    csv_path = f"E:/data6/ind-spacevtime/SGabor/Data/{pid}_SGabor.csv"

    # Load existing CSV if session > 0
    if session > 0:
        data = pd.read_csv(csv_path)
        if session > 1:
        # Load contrast value from last session
            with open(csv_path, 'r') as f:
                last_line = f.readlines()[-1]
                contrast1 = float(last_line.strip().split(',')[-2])
                contrast2 = float(last_line.strip().split(',')[-1])

    # If session 0, initialize new DataFrame and save empty CSV
    if session == 0:
        data = pd.DataFrame(columns=["session", "trial", "staircase", "orientation", "response", "correct", "contrast1", "contrast2"])
        data.to_csv(csv_path, index=False)

    FixationFrame = 80
    StimFrame = 80

    def GaborImage(ori, contrast=0.15, size=512, sf=5, decay=0.25):
        x = np.linspace(-1, 1, size)
        y = np.linspace(-1, 1, size)
        X, Y = np.meshgrid(x, y)

        theta = np.deg2rad(-45) if ori == 'left' else np.deg2rad(45)
        X_rot = X * np.cos(theta) + Y * np.sin(theta)
        phase = np.random.uniform(0, 2 * np.pi)

        grating = contrast * np.cos(2 * np.pi * sf * X_rot + phase)
        gauss = np.exp(-(X**2 + Y**2) / (2 * decay**2))
        gabor = np.clip(grating * gauss, -1, 1)
        return gabor

    def GaborStimulus(ori, contrast, noise_mean=0.0, noise_std=0.4, size=512):
        gabor = GaborImage(ori, contrast)
        squeeze_size = size // 8
        squeeze_noise = np.random.normal(loc=noise_mean, scale=noise_std, size=(squeeze_size, squeeze_size))
        noise = np.repeat(np.repeat(squeeze_noise, 8, axis=0), 8, axis=1)
        noise = np.clip(noise, -1, 1)
        return np.clip(gabor + noise, -1, 1)

    # Visual Setup
    win = visual.Window(size=(1920, 1200), color=0, units="pix", fullscr=True)
    stim = visual.ImageStim(win, size=(512, 512), units="pix")

    # Welcome Screen
    text = visual.TextStim(win, text="Welcome to the experiment! \n Press the SPACE key to begin the instruction", font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=2000,units="pix")
    text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    # Instruction Screen
    text = visual.TextStim(win, text="In this experiment, you will see a grating embedded within visual noise. \n The grating will either point up and to the RIGHT, or up and to the LEFT.\
    \n\nThe example below points up and to the LEFT.\
    \n\nPress the 'x' key if you think the grating is pointing up and to the LEFT. \n Press the 'm' key if you think the grating is pointing up and to the RIGHT.\
    \n\nWhen you are done reviewing the instructions, press the SPACE key to continue.", font="Dejavusans-bold", color=1.0, height=24, pos=(0,300), wrapWidth=2000,units="pix")
    example_image = visual.ImageStim(image=np.flipud(GaborStimulus(ori='left', contrast=0.6)), win=win, size=(512, 512), pos=(0, -200), units="pix")
    text.draw()
    example_image.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    # Practice trials
    if session == 0:
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
            practice_contrast = random.choice(contrast_practice)
            stim.image = np.flipud(GaborStimulus(ori=ori, contrast=practice_contrast))

            frames = [fixation, stim]
            frameDurations = [FixationFrame, StimFrame]
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
            if keys:
                print('asdadasds')
            response = 'left' if keys[0] == 'x' else 'right'
            correct = response == ori

            feedback_text = "Correct!" if correct else "Wrong!"
            feedback_color = 'green' if correct else 'red'
            feedback = visual.TextStim(win, text=feedback_text, color=feedback_color, height=36)
            feedback.draw()
            win.flip()
            if correct:
                correctSound1.play()
                core.wait(0.1)
                correctSound2.play()
            else:
                errorSound.play()
            core.wait(0.5)
            win.flip()
            core.wait(0.5)

    else:
        # Main block for session > 0
        text = visual.TextStim(win, text=f"Main Experiment (Session {session})\n\nPress the SPACE key to begin the trial block.", font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=2000,units="pix")
        text.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

        for trial in range(int(n_trials/2)):
            if 'escape' in event.getKeys():
                print("Experiment aborted by user.")
                break

            # 2D1U case
            fixation = visual.TextStim(win, text="+", color=1.0, height=48)
            ori = random.choice(oris)
            stim.image = np.flipud(GaborStimulus(ori=ori, contrast=contrast1))

            frames = [fixation, stim]
            frameDurations = [FixationFrame, StimFrame]
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
                correctSound1.play()
                core.wait(0.1)
                correctSound2.play()
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
                "contrast1": round(contrast1,2),
                "contrast2": round(contrast2,2)
            }

            # Staircase logic
            if correct:
                correct_counter1 += 1
                if correct_counter1 == 2:
                    contrast1 = max(0, contrast1 - step_size)
                    correct_counter1 = 0
            else:
                contrast1 += step_size
                correct_counter1 = 0

            core.wait(0.5)

            # 3D1U case
            fixation = visual.TextStim(win, text="+", color=1.0, height=48)
            ori = random.choice(oris)
            stim.image = np.flipud(GaborStimulus(ori=ori, contrast=contrast2))

            frames = [fixation, stim]
            frameDurations = [FixationFrame, StimFrame]
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
                correctSound1.play()
                core.wait(0.1)
                correctSound2.play()
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
                "contrast1": round(contrast1,2),
                "contrast2": round(contrast2,2)
            }

            # Staircase logic
            if correct:
                correct_counter2 += 1
                if correct_counter2 == 3:
                    contrast2 = max(0, contrast2 - step_size)
                    correct_counter2 = 0
            else:
                contrast2 += step_size
                correct_counter2 = 0

            core.wait(0.5)
    # Save updated data (including empty CSV from session 0)
    win.close()
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    
