from psychopy import visual, event, core, sound 
import sys
import numpy as np
import random
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from numpy.fft import fft2, ifft2, fftshift, ifftshift
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib

def runSL(session, pid, n_practices, n_trials):

    trialClock = core.Clock()

    correctSound1 = sound.Sound(value=600, secs=0.1)
    correctSound2 = sound.Sound(value=800, secs=0.1)
    errorSound = sound.Sound(value=500, secs=0.2)

    letters = ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L']
    alpha1 = 0.15
    alpha2 = 0.15
    alpha_practice = [0.15, 0.20, 0.25]
    step_size = 0.01
    correct_counter1 = 0
    correct_counter2 = 0

    FixationFrame = 80
    StimFrame = 80

    csv_path = f"E:/data6/ind-spacevtime/SLetter/Data/{pid}_SLetter.csv"

    # Load existing CSV if session > 0
    if session > 0:
        data = pd.read_csv(csv_path)
        if session > 1:
        # Load contrast value from last session
            with open(csv_path, 'r') as f:
                last_line = f.readlines()[-1]
                alpha1 = float(last_line.strip().split(',')[-2])
                alpha2 = float(last_line.strip().split(',')[-1])
                
    # If session 0, initialize CSV with header only (no data)
    if session == 0:
        data = pd.DataFrame(columns=["session", "trial","staircase", "letter", "response", "correct", "alpha1", "alpha2"])
        data.to_csv(csv_path, index=False)


    def LetterImage(letter, image_size=128, letter_size=64, bg_color=0.5, letter_color=1):
        bg_color = int(bg_color * 255) if 0 <= bg_color <= 1 else bg_color
        letter_color = int(letter_color * 255) if 0 <= letter_color <= 1 else letter_color
        image = Image.new('L', (image_size, image_size), color=bg_color)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("E:/data6/ind-spacevtime/TLetter/DejaVuSans-Bold.ttf", letter_size)
        bbox = draw.textbbox((0, 0), letter, font=font)
        letter_w, letter_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        image_w, image_h = image.size
        x = (image_w - letter_w) // 2 - bbox[0]
        y = (image_h - letter_h) // 2 - bbox[1]
        draw.text((x, y), letter, font=font, fill=letter_color)
        return np.array(image).astype(np.float32)

    def AddNoise(image, letters=letters, sigma=30, alpha=0.1):
        letter_list = [LetterImage(letter=l) for l in letters]
        letter_mean = np.mean(letter_list, axis=0)
        F = fftshift(fft2(letter_mean))
        freq_noise = np.random.normal(0, sigma, size=F.shape) + 1j * np.random.normal(0, sigma, size=F.shape)
        F = F * freq_noise
        letter_noise = np.real(ifft2(ifftshift(F)))
        letter_noise = (letter_noise - letter_noise.min()) / (letter_noise.max() - letter_noise.min()) * 255
        return alpha * image + (1 - alpha) * letter_noise 

    def LetterStimulus(letter, alpha=0.1):
        letter_image = AddNoise(LetterImage(letter), alpha=alpha)
        return letter_image

    def Norm(image):
        return 2 * (image / 255) - 1

    win = visual.Window(size=(1920, 1200), color=0, units="pix", fullscr=True)
    stim = visual.ImageStim(win, size=(512, 512), units="pix")

    # Welcome Screen
    text = visual.TextStim(win, text="Welcome to the experiment! \n Press the SPACE key to begin the instruction", font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=2000,units="pix")
    text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    # Instruction Screen
    text = visual.TextStim(win, text="In this experiment, you will see a letter of the alphabet embedded in visual noise. \n The letter will be chosen from the second row of the keyboard - [A,S,D,F,G,H,J,K,L]\n"
                                    "The example below is the letter A.\n\nYour task is to identify the letter after it is presented at the center of the screen.\n"
                                    "Press the letter you think you see using the second row of the keyboard. It will be quick, so pay attention.\n\nPress the SPACE key when you are done reviewing the instructions.", font="Dejavusans-bold", color=1.0, height=24, pos=(0,300), wrapWidth=2000,units="pix")
    text.draw()
    image = visual.ImageStim(image=np.flipud(Norm(LetterStimulus(letter='A', alpha=0.12))), win=win, size=(512, 512), pos=(0, -200), units="pix")
    image.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    if session == 0:
        # Practice trials with feedback
        text = visual.TextStim(win, text= "You will now be given several practice trials. \n You will be given feedback after each trial.\n\n"
                                        "Choose the letter you think you see form the second row of the keyboard.\nPress SPACE to begin the practice trials.", font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=2000,units="pix")
        text.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

        for trial in range(n_practices):
            if 'escape' in event.getKeys():
                print("Experiment aborted by user.")
                break

            fixation = visual.TextStim(win, text="+", color=1.0, height=48)
            letter = random.choice(letters)
            practice_alpha = random.choice(alpha_practice)
            stim.image = np.flipud(Norm(LetterStimulus(letter, alpha=practice_alpha)))

            frames = [fixation, stim]
            frameDurations = [FixationFrame, StimFrame]
            exlib.runFrames(win, frames, frameDurations, trialClock)

            wait = visual.TextStim(win, text="", color=1.0, height=48)
            wait.draw()
            win.flip()
            keys = event.getKeys(keyList=[l.lower() for l in letters] + ['escape'])
            if len(keys) == 0:
                keys = event.waitKeys(keyList=[l.lower() for l in letters] + ['escape'])
            if 'escape' in keys:
                print("Experiment aborted by user.")
                break
            response = keys[0].upper()
            correct = response == letter

            if correct:
                feedback = visual.TextStim(win, text="Correct!", color='green', height=36)
                feedback.draw()
                win.flip()
                correctSound1.play()
                core.wait(0.1)
                correctSound2.play()
                core.wait(0.4)
            else:
                feedback = visual.TextStim(win, text=f"Wrong! The correct letter was: {letter}", color='red', height=36)
                feedback.draw()
                win.flip()
                errorSound.play()
                core.wait(0.5)
            win.flip()
            core.wait(0.5)

    else:
        # Main experiment block
        text = visual.TextStim(win, text=f"Main Experiment (Session {session})\n"
                                        "Choose the letter you think you see from the second row of the keyboard.\n\nPress SPACE to begin trials.", font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=2000,units="pix")
        text.draw()
        win.flip()
        event.waitKeys(keyList=['space'])


        for trial in range(int(n_trials/2)):
            if 'escape' in event.getKeys():
                print("Experiment aborted by user.")
                break

            # 2D1U
            fixation = visual.TextStim(win, text="+", color=1.0, height=48)
            letter = random.choice(letters)
            stim.image = np.flipud(Norm(LetterStimulus(letter, alpha=alpha1)))

            frames = [fixation, stim]
            frameDurations = [FixationFrame, StimFrame]
            exlib.runFrames(win, frames, frameDurations, trialClock)

            wait = visual.TextStim(win, text="", color=1.0, height=48)
            wait.draw()
            win.flip()
            keys = event.getKeys(keyList=[l.lower() for l in letters] + ['escape'])
            if len(keys) == 0:
                keys = event.waitKeys(keyList=[l.lower() for l in letters] + ['escape'])
            if 'escape' in keys:
                print("Experiment aborted by user.")
                break
            response = keys[0].upper()
            correct = response == letter

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
                "letter": letter,
                "response": response,
                "correct": correct,
                "alpha1": round(alpha1,2),
                "alpha2": round(alpha2,2)
            }

            if correct:
                correct_counter1 += 1
                if correct_counter1 == 2:
                    alpha1 = max(0, alpha1 - step_size)
                    correct_counter1 = 0
            else:
                alpha1 = min(1.0, alpha1 + step_size)
                correct_counter1 = 0

            core.wait(0.5)

            # 3D1U
            fixation = visual.TextStim(win, text="+", color=1.0, height=48)
            letter = random.choice(letters)
            stim.image = np.flipud(Norm(LetterStimulus(letter, alpha=alpha2)))

            frames = [fixation, stim]
            frameDurations = [FixationFrame, StimFrame]
            exlib.runFrames(win, frames, frameDurations, trialClock)

            wait = visual.TextStim(win, text="", color=1.0, height=48)
            wait.draw()
            win.flip()
            keys = event.getKeys(keyList=[l.lower() for l in letters] + ['escape'])
            if len(keys) == 0:
                keys = event.waitKeys(keyList=[l.lower() for l in letters] + ['escape'])
            if 'escape' in keys:
                print("Experiment aborted by user.")
                break
            response = keys[0].upper()
            correct = response == letter

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
                "letter": letter,
                "response": response,
                "correct": correct,
                "alpha1": round(alpha1,2),
                "alpha2": round(alpha2,2)
            }

            if correct:
                correct_counter2 += 1
                if correct_counter2 == 3:
                    alpha2 = max(0, alpha2 - step_size)
                    correct_counter2 = 0
            else:
                alpha2 = min(1.0, alpha2 + step_size)
                correct_counter2 = 0 

            core.wait(0.5)

    win.close()
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    