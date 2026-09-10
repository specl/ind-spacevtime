from psychopy import visual, event, core, sound 
import sys
import numpy as np
import matplotlib.pyplot as plt
import random
import pandas as pd
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib
import cv2

def runTP(session, pid, n_practices, n_trials):
    
    # region
    trialClock = core.Clock()
    # endregion
    correctSound1 = sound.Sound(value=600, secs=0.1)
    correctSound2 = sound.Sound(value=800, secs=0.1)
    errorSound = sound.Sound(value=500, secs=0.2)

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
    csv_path = f"E:/data6/ind-spacevtime/TPi/Data/{pid}_TPi.csv"

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
    NoiseFrame = 8

    def ShowImage(image):
        plt.imshow(image, cmap='gray', vmin=0, vmax=1)
        plt.axis('off')
        plt.show()

    def PiImage(ori=None, diff=10, size=128):
        fixed_length, leg_width, bar_height = 80, 1, 2
        Pi = np.zeros((size, size)) 

        spacing = size // 2 - 15
        left_x = spacing
        right_x = size - spacing - leg_width
        bar_y = int(size * 1/4) 

        fixed_length + np.random.uniform(-20,20)

        if ori is None:
            right_len = fixed_length + diff * 3
            left_len = fixed_length + diff * 3
        elif ori == 'right':
            right_len = fixed_length + diff
            left_len = fixed_length
        elif ori == 'left':
            right_len = fixed_length
            left_len = fixed_length + diff

        Pi[bar_y:bar_y + left_len // 2, left_x:left_x + leg_width] = 1
        Pi[bar_y:bar_y + right_len // 2, right_x:right_x + leg_width] = 1

        bar_y1 = bar_y - bar_height // 2
        bar_y2 = bar_y + bar_height // 2
        Pi[bar_y1:bar_y2, left_x + leg_width:right_x] = 1 

        return Pi.astype(np.float32)

    def PiMask(size=128, num_shapes=20):
        mask = np.zeros((size, size))
        spacing = size // 3 + 10
        left_x = spacing
        right_x = size - spacing 

        for _ in range(num_shapes):
            for x_base in [left_x, right_x]:
                # Choose a tilt angle (in radians) between -45° and -10° or 10° and 45°
                if np.random.rand() < 0.5:
                    angle_deg = np.random.uniform(-45,-10)
                else:
                    angle_deg = np.random.uniform(10,45)
                angle_rad = np.deg2rad(angle_deg)

                y1 = np.random.randint(20, size - 40)
                length = np.random.randint(5, 20)

                dx = int(np.sin(angle_rad) * length)
                dy = int(np.cos(angle_rad) * length)

                x1 = x_base + np.random.randint(-5, 5)
                x2 = x1 + dx
                y2 = y1 + dy

                cv2.line(mask, (x1, y1), (x2, y2), 1, thickness=1)

        for _ in range(num_shapes // 2):
            x1 = np.random.randint(left_x, right_x)
            y1 = np.random.randint(size // 6, size // 4)
            length = np.random.randint(5, 15)
            if np.random.rand() < 0.5:
                angle_deg = np.random.uniform(-45,-10)
            else:
                angle_deg = np.random.uniform(10,45)
            angle_rad = np.deg2rad(angle_deg)

            dx = int(np.cos(angle_rad) * length)
            dy = int(np.sin(angle_rad) * length)

            x2 = x1 + dx
            y2 = y1 + dy
            cv2.line(mask, (x1, y1), (x2, y2), 1, thickness=1)

        return mask

    def Norm(image):
        return 2 * image - 1

    # Visual Setup
    win = visual.Window(size=(1920, 1200), color=-1, units="pix", fullscr=True)
    stim = visual.ImageStim(win, size=(512, 512), units="pix")

    # Welcome Screen
    text = visual.TextStim(win, text="Welcome to the experiment! \n Press the SPACE key to begin the instruction", font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=1000,units="pix")
    text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    # Instruction Screen
    instruction_text =(
        "In this experiment, you will see a Pi-shape, followed by random lines on top of the shape.\n"
        "The two legs of the Pi will be different lengths.\n"
        "Your task is to identify which leg is longer after the Pi is presented.\n"
        "If you think the LEFT leg is longer, press the 'x' key. If you think the the RIGHT leg is longer, press the 'm' key.\n\n"
        "In the example below, the LEFT leg is longer \n\n"
        "Press the SPACE key to continue.")
    
    text = visual.TextStim(win, text=instruction_text, font="Dejavusans-bold", color=1.0, height=24, pos=(0,300), wrapWidth=2000,units="pix")
    text.draw()
    image = visual.ImageStim(image=np.flipud(Norm(PiImage(ori='left'))), win=win, size=(512, 512), pos=(0, -250), units="pix")
    image.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    if session == 0:
        # Practice trials instructions
        practice_text= "You will now be given several practice trials. \n You will be given feedback after each trial.\n\n Press the 'x' key if you think the LEFT leg is longer or the 'm' key if you think the RIGHT leg is longer.\nPress SPACE to start the practice trials."
        text = visual.TextStim(win, text=practice_text, font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=2000,units="pix")
        text.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

        for trial in range(n_practices):
            if 'escape' in event.getKeys():
                print("Experiment aborted during practice.")
                break

            fixation = visual.TextStim(win, text="+", color=1.0, height=48)

            ori, practice_soa = random.choice(oris), random.choice(soa_practice)
            stim.image = np.flipud(Norm(PiImage(ori=ori)))

            noise_frames = [visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(Norm(PiMask()))) for _ in range(5)]
            
            frames = [fixation, stim] + noise_frames
            frameDurations = [FixationFrame, practice_soa] + [NoiseFrame]*5
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
                feedback_text = "Correct!"
                feedback_color = 'green'
                feedback = visual.TextStim(win, text=feedback_text, color=feedback_color, height=36)
                feedback.draw()
                win.flip()
                correctSound1.play()
                core.wait(0.1)
                correctSound2.play()
                core.wait(0.4)
            else:
                feedback_text = "Wrong!"
                feedback_color = 'red'
                feedback = visual.TextStim(win, text=feedback_text, color=feedback_color, height=36)
                feedback.draw()
                win.flip()
                errorSound.play()
                core.wait(0.5)

            win.flip()
            core.wait(0.5)

    else:
        # Main Staircase Block
        main_text= f"Main Experiment (Session {session}): \n\n Press the 'x' key if you think the LEFT leg is longer or the 'm' key if you think the RIGHT leg is longer.\nPress SPACE to begin the trial block."
        text = visual.TextStim(win, text=main_text, font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=2000,units="pix")
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
            stim.image = np.flipud(Norm(PiImage(ori=ori)))

            noise_frames = [visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(Norm(PiMask()))) for _ in range(5)]
            
            frames = [fixation, stim] + noise_frames
            frameDurations = [FixationFrame, soa1] + [NoiseFrame]*5
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
            stim.image = np.flipud(Norm(PiImage(ori=ori)))

            noise_frames = [visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(Norm(PiMask()))) for _ in range(5)]
            
            frames = [fixation, stim] + noise_frames
            frameDurations = [FixationFrame, soa2] + [NoiseFrame]*5
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


    win.close()

    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
