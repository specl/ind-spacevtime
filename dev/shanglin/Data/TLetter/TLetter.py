from psychopy import visual, event, core, sound 
import sys
import numpy as np
import random
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from numpy.fft import fft2, ifft2, fftshift, ifftshift
sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib

def runTL(session, pid, n_practices, n_trials):
    # region
    trialClock = core.Clock()
    # endregion

    correctSound1 = sound.Sound(value=600, secs=0.1)
    correctSound2 = sound.Sound(value=800, secs=0.1)
    errorSound = sound.Sound(value=500, secs=0.2)

    # Parameters
    letters = ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L']
    soa1 = 12
    soa2 = 12
    soa_practice = [12, 14, 16]
    step_size = 1
    correct_counter1 = 0
    correct_counter2 = 0
    data = []

    csv_path = f"E:/data6/ind-spacevtime/TLetter/Data/{pid}_TLetter.csv"

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
        data = pd.DataFrame(columns=["session", "trial","staircase", "letter", "response", "correct", "soa1", "soa2"])
        data.to_csv(csv_path, index=False)


    FixationFrame = 80
    NoiseFrame = 8

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

        draw.text((x, y), letter, font=font, fill=letter_color * 255)

        return np.array(image).astype(np.float32)

    def Noise(letters=['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'], sigma=30):
        letter_list = [LetterImage(letter=l) for l in letters]
        letter_mean = np.mean(letter_list, axis=0)
        F = fftshift(fft2(letter_mean))
        freq_noise = np.random.normal(0, sigma, size=F.shape) + 1j * np.random.normal(0, sigma, size=F.shape)
        F = F * freq_noise
        letter_noise = np.real(ifft2(ifftshift(F)))
        letter_noise = (letter_noise - letter_noise.min()) / (letter_noise.max() - letter_noise.min()) * 255
        return letter_noise

    def NormLetter(image):
        return ((image - 127) / 127) * 0.05

    def NormNoise(image):
        return 2 * (image / 255) - 1

    # Visual Setup
    win = visual.Window(size=(1920, 1200), color=0, units="pix", fullscr=True)
    stim = visual.ImageStim(win, size=(512, 512), units="pix")

    # Welcome Screen
    text = visual.TextStim(win, text="Welcome to the experiment! \n Press the SPACE key to begin the instruction", font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=1000,units="pix")
    text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    # Instruction Screen
    text = visual.TextStim(win, text="In this experiment, you will see a letter of the alphabet, followed by visual noise. \n The letter will be chosen from the second row of the keyboard - [A,S,D,F,G,H,J,K,L]\n"
                                    "The example below is the letter A.\n\nYour task is to identify the letter after it is presented at the center of the screen.\n"
                                    "Press the letter you think you see using the second row of the keyboard. It will be quick, so pay attention.\n\nPress the SPACE key when you are done reviewing the instructions.", font="Dejavusans-bold", color=1.0, height=24, pos=(0,300), wrapWidth=2000,units="pix")
    text.draw()
    image = visual.ImageStim(image=np.flipud(NormLetter(LetterImage(letter='A'))), win=win, size=(512, 512), pos=(0, -200), units="pix")
    image.draw()
    win.flip()
    event.waitKeys(keyList=['space'])

    if session == 0:

        # Practice trail screen
        text = visual.TextStim(win, text= "You will now be given several practice trials. \n You will be given feedback after each trial.\n\n"
                                        "Choose the letter you think you see form the second row of the keyboard.\nPress SPACE to begin the practice trials.", font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=2000,units="pix")
        text.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

        # Trial Loop
        for trial in range(n_practices):
            #if 'escape' in event.getKeys():
            #   print("Experiment aborted by user.")
            #   break

            fixation = visual.TextStim(win, text="+", color=1.0, height=48)

            letter, practice_soa = random.choice(letters), random.choice(soa_practice)
            stim.image = np.flipud(NormLetter(LetterImage(letter)))

            noise_frames = [visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(NormNoise(Noise()))) for _ in range(5)]

            frames = [fixation, stim] + noise_frames
            frameDurations = [FixationFrame, practice_soa] + [NoiseFrame]*5
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
            
            #keys = event.waitKeys(keyList=[[letters],'escape'])
            #if 'escape' in keys:
             #   print("Experiment aborted by user.")
             #   break
            else:
                win.flip()
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
        # --- Main Staircase Block ---
        text = visual.TextStim(win, text=f"Main Experiment (Session {session})\n"
                                        "Choose the letter you think you see from the second row of the keyboard.\n\nPress SPACE to begin trials.", font="Dejavusans-bold", color=1.0, height=24, pos=(0,0), wrapWidth=2000,units="pix")

        text.draw()
        win.flip()
        event.waitKeys(keyList=['space'])

        for trial in range(round(n_trials/2)):
            if 'escape' in event.getKeys():
                print("Experiment aborted by user.")
                break

            # 2D1U
            fixation = visual.TextStim(win, text="+", color=1.0, height=48)

            letter = random.choice(letters)
            stim.image = np.flipud(NormLetter(LetterImage(letter)))

            noise1 = visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(NormNoise(Noise())))
            noise2 = visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(NormNoise(Noise())))
            noise3 = visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(NormNoise(Noise())))
            noise4 = visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(NormNoise(Noise())))
            noise5 = visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(NormNoise(Noise())))

            frames = [fixation, stim, noise1, noise2, noise3, noise4, noise5]
            frameDurations = [FixationFrame,soa1,NoiseFrame, NoiseFrame, NoiseFrame, NoiseFrame, NoiseFrame]

            exlib.runFrames(win, frames, frameDurations, trialClock)
            #exlib runframes broke here on main 2 start -lily

            wait = visual.TextStim(win, text="", color=1.0, height=48)
            wait.draw()
            win.flip()
            keys = event.getKeys(keyList=[l.lower() for l in letters] + ['escape'])
            if len(keys) == 0:
                keys = event.waitKeys(keyList=[l.lower() for l in letters] + ['escape'])
            if 'escape' in keys:
                print("Experiment aborted by user.")
                break
            win.flip()
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
                "staircase":2, 
                "letter": letter,
                "response": response,
                "correct": correct,
                "soa1": soa1,
                "soa2": soa2
                }

            if correct:
                correct_counter1 += 1
                if correct_counter1 == 2:
                    soa1 = max(0, soa1 - step_size)
                    correct_counter1 = 0
            else:
                soa1 += step_size
                correct_counter1 = 0
            core.wait(0.5)

            # 3D1U
            fixation = visual.TextStim(win, text="+", color=1.0, height=48)

            letter = random.choice(letters)
            stim.image = np.flipud(NormLetter(LetterImage(letter)))

            noise1 = visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(NormNoise(Noise())))
            noise2 = visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(NormNoise(Noise())))
            noise3 = visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(NormNoise(Noise())))
            noise4 = visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(NormNoise(Noise())))
            noise5 = visual.ImageStim(win, size=(512, 512), units="pix", image=np.flipud(NormNoise(Noise())))

            frames = [fixation, stim, noise1, noise2, noise3, noise4, noise5]
            frameDurations = [FixationFrame,soa2,NoiseFrame, NoiseFrame, NoiseFrame, NoiseFrame, NoiseFrame]

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
            win.flip()
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
                "soa1": soa1,
                "soa2": soa2
                }

            if correct:
                correct_counter2 += 1
                if correct_counter2 == 3:
                    soa2 = max(0, soa2 - step_size)
                    correct_counter2 = 0
            else:
                soa2 += step_size
                correct_counter2 = 0
            core.wait(0.5)

    win.close()
    data.to_csv(csv_path, index=False)
