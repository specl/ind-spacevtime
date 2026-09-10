from psychopy import visual, event, core, sound
import numpy as np
import random
import pandas as pd
import cv2
import sys
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib

def runSP(session, pid, n_practices, n_trials):

    correctSound1 = sound.Sound(value=600, secs=0.1)
    correctSound2 = sound.Sound(value=800, secs=0.1)
    errorSound = sound.Sound(value=500, secs=0.2)

    trialClock = core.Clock()

    # Parameters
    oris = ['left', 'right']
    diff1 = 15  # initial difficulty parameter
    diff2 = 15 
    diff_practice = [15, 20, 25]
    step_size = 1
    correct_counter1 = 0
    correct_counter2 = 0
    data = []

    csv_path = f"E:/data6/ind-spacevtime/SPi/Data/{pid}_SPi.csv"

    # Load existing CSV if session > 0
    if session > 0:
        data = pd.read_csv(csv_path)
        if session > 1:
        # Load contrast value from last session
            with open(csv_path, 'r') as f:
                last_line = f.readlines()[-1]
                diff1 = float(last_line.strip().split(',')[-2])
                diff2 = float(last_line.strip().split(',')[-1])
                
    # If session 0, initialize CSV with header only (no data)
    if session == 0:
        data = pd.DataFrame(columns=["session", "trial","staircase", "orientation", "response", "correct", "diff1", "diff2"])
        data.to_csv(csv_path, index=False)

    FixationFrame = 80
    StimFrame = 80

    def Norm(image):
        return 2 * image - 1

    def PiImage(ori=None, diff=10, size=128):
        fixed_length, leg_width, bar_height = 80, 1, 2
        Pi = np.zeros((size, size))

        spacing = size // 2 - 15
        left_x = spacing
        right_x = size - spacing - leg_width
        bar_y = int(size * 1 / 4)

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

    def AddNoise(image, num_shapes=30):
        size = image.shape[0]
        mask = np.zeros((size, size), dtype=np.uint8)
        spacing = size // 3 + 10
        left_x = spacing
        right_x = size - spacing

        for _ in range(num_shapes):
            for x_base in [left_x, right_x]:
                if np.random.rand() < 0.5:
                    angle_deg = np.random.uniform(-45, -10)
                else:
                    angle_deg = np.random.uniform(10, 45)
                angle_rad = np.deg2rad(angle_deg)

                y1 = np.random.randint(20, size - 40)
                length = np.random.randint(5, 20)

                dx = int(np.sin(angle_rad) * length)
                dy = int(np.cos(angle_rad) * length)

                x1 = x_base + np.random.randint(-5, 5)
                x2 = x1 + dx
                y2 = y1 + dy

                cv2.line(mask, (x1, y1), (x2, y2), 255, thickness=1)

        for _ in range(num_shapes // 2):
            x1 = np.random.randint(left_x, right_x)
            y1 = np.random.randint(size // 6, size // 4)
            length = np.random.randint(5, 15)

            if np.random.rand() < 0.5:
                angle_deg = np.random.uniform(-45, -10)
            else:
                angle_deg = np.random.uniform(10, 45)
            angle_rad = np.deg2rad(angle_deg)

            dx = int(np.cos(angle_rad) * length)
            dy = int(np.sin(angle_rad) * length)

            x2 = x1 + dx
            y2 = y1 + dy
            cv2.line(mask, (x1, y1), (x2, y2), 255, thickness=1)

        noisy = np.clip(image + mask, 0, 1)
        return noisy

    def PiStimulus(ori, diff):
        Pi_image = AddNoise(PiImage(ori=ori, diff=diff))
        return Pi_image

    win = visual.Window(size=(1920, 1200), color=-1, units="pix", fullscr=True)
    stim = visual.ImageStim(win, size=(512, 512), units="pix")

    # Welcome Screen
    text = visual.TextStim(win, text="Welcome to the experiment! \n Press the SPACE key to begin the instruction", font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=2000,units="pix")
    text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    # Instruction Screen
    instruction_text = (
        "In this experiment, you will see a Pi-shape buried by many lines.\n"
        "The two legs of the Pi will be different lengths.\n"
        "Your task is to identify which leg is longer after the Pi is presented.\n"
        "If you think the LEFT leg is longer, press the 'x' key. If you think the the RIGHT leg is longer, press the 'm' key.\n\n"
        "In the example below, the LEFT leg is longer \n\n"
        "Press the SPACE key to continue."
    )
    text = visual.TextStim(win, text=instruction_text, font="Dejavusans-bold", color=1.0, height=24, pos=(0,300), wrapWidth=2000,units="pix")
    text.draw()
    example_image = visual.ImageStim(image=np.flipud(Norm(PiStimulus(ori='left', diff=15))), win=win, size=(512, 512), pos=(0, -200), units="pix")
    example_image.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    if session == 0:
        # Practice trials with feedback (do NOT save practice data)
        practice_text = "You will now be given several practice trials. \n You will be given feedback after each trial.\n\n Press the 'x' key if you think the LEFT leg is longer or the 'm' key if you think the RIGHT leg is longer.\nPress SPACE to start the practice trials."
        text = visual.TextStim(win, text=practice_text, font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=2000,units="pix")
        text.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

        for trial in range(n_practices):
            if 'escape' in event.getKeys():
                print("Experiment aborted during practice.")
                break

            fixation = visual.TextStim(win, text="+", color=1.0, height=48)
            ori = random.choice(oris)
            practice_diff = random.choice(diff_practice)
            stim.image = np.flipud(Norm(PiStimulus(ori=ori, diff=practice_diff)))

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
                print("Experiment aborted during practice.")
                break

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
        # Main experiment block for session > 0
        main_text = f"Main Experiment (Session {session}): \n\n Press the 'x' key if you think the LEFT leg is longer or the 'm' key if you think the RIGHT leg is longer.\nPress SPACE to begin the trial block."
        text = visual.TextStim(win, text=main_text, font="Dejavusans-bold", color=1.0, height=24, pos=(0,300), wrapWidth=2000,units="pix")
        text.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

        for trial in range(int(n_trials/2)):
            if 'escape' in event.getKeys():
                print("Experiment aborted by user.")
                break

            # 2D1U
            fixation = visual.TextStim(win, text="+", color=1.0, height=48)
            ori = random.choice(oris)
            stim.image = np.flipud(Norm(PiStimulus(ori=ori, diff=round(diff1))))
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

            # Save trial data
            data.loc[len(data)] = {
                "session": session,
                "trial": trial + 1,
                "staircase": 2,
                "orientation": ori,
                "response": response,
                "correct": correct,
                "diff1": round(diff1),
                "diff2": round(diff2)
            }

            # Staircase logic
            if correct:
                correct_counter1 += 1
                if correct_counter1 == 2:
                    diff1 = max(0, diff1 - step_size)
                    correct_counter1 = 0
            else:
                diff1 += step_size
                correct_counter1 = 0

            core.wait(0.5)

            # 3D1U
            fixation = visual.TextStim(win, text="+", color=1.0, height=48)
            ori = random.choice(oris)
            stim.image = np.flipud(Norm(PiStimulus(ori=ori, diff=round(diff2))))
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

            # Save trial data
            data.loc[len(data)] = {
                "session": session,
                "trial": trial + 1,
                "staircase": 3,
                "orientation": ori,
                "response": response,
                "correct": correct,
                "diff1": round(diff1),
                "diff2": round(diff2)
            }

            # Staircase logic
            if correct:
                correct_counter2 += 1
                if correct_counter2 == 3:
                    diff2 = max(0, diff2 - step_size)
                    correct_counter2 = 0
            else:
                diff2 += step_size
                correct_counter2 = 0

            core.wait(0.5)


    data.to_csv(csv_path, index=False)
    win.close()
    