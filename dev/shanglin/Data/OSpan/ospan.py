
from psychopy import visual, core, event
import random
import numpy as np
import csv
import os
import sys

sys.path.insert(0, 'E:/lib/data6')
import expLib61 as exlib

# =========================
# Config & Globals
# =========================
WIN_SIZE = (1920, 1080)
FULLSCR = True
UNITS = "pix"

LETTER_DURATION = 0.800  # seconds
FEEDBACK_DURATION = 2.000

MATH_PRACTICE_TRIALS = 15
SET_SIZES = [3, 4, 5, 6, 7]
SETS_PER_SIZE = 3

LETTER_SET = ["F","H","J","K","L","N","P","Q","R","S","T","Y"]
ACCURACY_CRITERION = 0.85

# Optional: a hard safety cap so people can’t stall forever on TRUE/FALSE
HARD_MAX_JUDGEMENT_TIME = None  # e.g., 30.0; set None to disable

# =========================
# Filenames & exlib
# =========================
refreshRate = 165
exlib.setRefreshRate(refreshRate)
pool = 3
dbConf = exlib.data6
expName = "indSVT"
[pid, sid, fname] = exlib.startExp(expName, dbConf, pool=pool, lockBox=True, refreshRate=refreshRate)

os.makedirs("Data", exist_ok=True)
os.makedirs("Data_summary", exist_ok=True)

triallog_path = os.path.abspath(f"Data/{pid}_OSpan.csv")
summary_path = os.path.abspath(f"Data_summary/{pid}_OSpan_summary.csv")

# =========================
# Window & IO
# =========================
win = visual.Window(size=WIN_SIZE, units=UNITS, fullscr=FULLSCR, color=(0,0,0))
mouse = event.Mouse(win=win, visible=True)

text_kwargs = dict(color='white', height=32, alignText='center', wrapWidth=1600)
small_text_kwargs = dict(color='white', height=24, alignText='center', wrapWidth=1600)
red_small_text_kwargs = dict(color='red', height=28, alignText='right')

msg = visual.TextStim(win, text='', **text_kwargs)
msg_small = visual.TextStim(win, text='', **small_text_kwargs)
acc_text = visual.TextStim(win, text='', **red_small_text_kwargs)

# =========================
# Utilities
# =========================
def check_escape():
    if 'escape' in event.getKeys(['escape']):
        win.close()
        core.quit()

def draw_accuracy_counts(running_correct, running_total):
    if running_total <= 0:
        acc_text.text = "100%"
    else:
        acc = running_correct / float(running_total)
        acc_text.text = f"{int(round(acc*100))}%"
    acc_text.pos = (win.size[0]//2 - 110, win.size[1]//2 - 60)
    acc_text.draw()

def show_instructions(text):
    mouse.clickReset()
    while True:
        check_escape()
        msg.text = text
        msg.draw()
        msg_small.text = "Click to continue"
        msg_small.pos = (0, -win.size[1]//2 + 100)
        msg_small.draw()
        win.flip()
        if mouse.getPressed()[0]:
            core.wait(0.2)
            return
        core.wait(0.01)

# =========================
# Button UI
# =========================
class Button:
    def __init__(self, win, text, pos, size=(220,70)):
        self.rect = visual.Rect(
            win,
            width=size[0], height=size[1], pos=pos,
            fillColor=(-0.2,-0.2,-0.2),
            lineColor=(0.7,0.7,0.7)
        )
        self.label = visual.TextStim(win, text=text, pos=pos, color='white', height=28)

    def draw(self):
        self.rect.draw()
        self.label.draw()

    def contains(self, mouse):
        return self.rect.contains(mouse)

def build_letter_grid(win, letters):
    cols, rows = 4, 3
    spacing_x, spacing_y = 220, 140
    origin_x = - (cols-1)/2 * spacing_x
    origin_y = + (rows-1)/2 * spacing_y
    buttons = []
    k = 0
    for r in range(rows):
        for c in range(cols):
            pos = (origin_x + c*spacing_x, origin_y - r*spacing_y)
            btn = Button(win, letters[k], pos, size=(100,80))
            buttons.append(btn)
            k += 1
    return buttons

# =========================
# Task elements
# =========================
def gen_math_problem():
    """Generate arithmetic and a shown answer.
    Returns: problem_str, correct_answer, shown_answer, is_true_display
    """
    ops = ['add','sub','mul','div']
    op = random.choice(ops)
    if op == 'add':
        a, b = random.randint(1,9), random.randint(1,9)
        correct = a + b
        prob = f"{a} + {b} = ?"
    elif op == 'sub':
        a, b = random.randint(2,9), random.randint(1,8)
        if b > a:
            a, b = b, a
        correct = a - b
        prob = f"{a} - {b} = ?"
    elif op == 'mul':
        a, b = random.randint(1,9), random.randint(1,9)
        correct = a * b
        prob = f"{a} * {b} = ?"
    else:  # div, integer result
        b = random.randint(1,9)
        correct = random.randint(1,9)
        a = b * correct
        prob = f"{a} / {b} = ?"

    is_true = random.random() < 0.5
    if is_true:
        shown = correct
    else:
        delta = random.choice([1,2,3])
        shown = correct + delta if random.random() < 0.5 else max(0, correct - delta)
        if shown == correct:
            shown += 1
    return prob, correct, shown, is_true

def math_problem_screen(problem_text, vis_correct, vis_total):
    clock = core.Clock()
    mouse.clickReset()
    while True:
        check_escape()
        msg.text = (
            "Solve mentally as quickly as you can:\n\n"
            f"{problem_text}\n\n"
            "Click the mouse once you've solved it to continue"
        )
        msg.draw()
        draw_accuracy_counts(vis_correct, vis_total)
        win.flip()
        if mouse.getPressed()[0]:
            rt = clock.getTime()
            core.wait(0.15)
            return rt
        core.wait(0.01)

def math_answer_screen(shown_answer, time_limit, vis_correct, vis_total, hard_max_time=None):
    """
    Keep speed-error detection (time_limit) BUT do not skip judgement.
    If clock > time_limit: speed_violation=True (record once), but keep waiting for response.
    Returns: resp_true (True/False or None if hard cap hit), rt, speed_violation (bool)
    """
    clock = core.Clock()
    true_btn = Button(win, "TRUE", pos=(-160, -200))
    false_btn = Button(win, "FALSE", pos=(160, -200))
    buttons = [true_btn, false_btn]
    mouse.clickReset()

    speed_violation = False

    while True:
        check_escape()

        t = clock.getTime()

        # mark speed error once, but DO NOT return/skip
        if (time_limit is not None) and (not speed_violation) and (t > time_limit + 2):
            speed_violation = True

        # optional hard cap (rarely needed)
        if (hard_max_time is not None) and (t > hard_max_time):
            return None, t, speed_violation

        msg.text = f"Proposed answer:\n\n{shown_answer}\n\nChoose TRUE or FALSE"
        msg.draw()
        for b in buttons:
            b.draw()
        draw_accuracy_counts(vis_correct, vis_total)

        if speed_violation:
            msg_small.text = "Too slow (speed error recorded). Please respond now."
            msg_small.pos = (0, -win.size[1]//2 + 120)
            msg_small.draw()

        win.flip()

        if mouse.getPressed()[0]:
            if true_btn.contains(mouse):
                rt = clock.getTime()
                core.wait(0.15)
                return True, rt, speed_violation
            if false_btn.contains(mouse):
                rt = clock.getTime()
                core.wait(0.15)
                return False, rt, speed_violation

        core.wait(0.01)

def present_letter(letter, vis_correct, vis_total):
    t0 = core.getTime()
    while core.getTime() - t0 < LETTER_DURATION:
        check_escape()
        msg.text = letter
        msg.draw()
        draw_accuracy_counts(vis_correct, vis_total)
        win.flip()

def recall_screen(set_size, vis_correct, vis_total):
    grid = build_letter_grid(win, LETTER_SET)
    blank_btn = Button(win, "blank", pos=(-240, -300))
    clear_btn = Button(win, "clear", pos=(0, -300))
    exit_btn = Button(win, "Exit", pos=(240, -300))
    recalled = []
    mouse.clickReset()

    while True:
        check_escape()
        msg_small.text = f"Select the letters in the order they were presented (remaining: {set_size - len(recalled)})"
        msg_small.pos = (0, 300)
        msg_small.draw()

        draw_accuracy_counts(vis_correct, vis_total)

        for b in grid:
            b.draw()
        for b in [blank_btn, clear_btn, exit_btn]:
            b.draw()

        curr = "".join([c if c is not None else "_" for c in recalled])
        msg.text = curr
        msg.pos = (0, 200)
        msg.draw()
        msg.pos = (0, 0)

        win.flip()

        if mouse.getPressed()[0]:
            if blank_btn.contains(mouse):
                if len(recalled) < set_size:
                    recalled.append(None)
                core.wait(0.15)
            elif clear_btn.contains(mouse):
                recalled = []
                core.wait(0.15)
            elif exit_btn.contains(mouse):
                break
            else:
                for i, b in enumerate(grid):
                    if b.contains(mouse):
                        if len(recalled) < set_size:
                            recalled.append(LETTER_SET[i])
                        core.wait(0.15)
                        break

        if len(recalled) >= set_size:
            break
        core.wait(0.01)

    while len(recalled) < set_size:
        recalled.append(None)
    return recalled

def feedback_screen(n_correct_in_set, set_size, math_errors_in_set):
    t_end = core.getTime() + FEEDBACK_DURATION
    while core.getTime() < t_end:
        check_escape()
        msg.text = (
            f"You recalled {n_correct_in_set} / {set_size} letters correctly\n"
            f"Math errors in this set: {math_errors_in_set}"
        )
        msg.draw()
        win.flip()

# =========================
# Scoring & Saving
# =========================
def compute_scores(trials_by_set, letters_presented_by_set, recalls_by_set, math_accuracy_errors_by_set, speed_errors_by_set):
    total_correct = 0
    absolute_score = 0
    math_accuracy_errors = 0
    math_speed_errors = 0

    for s, set_size in enumerate(trials_by_set):
        presented = letters_presented_by_set[s]
        recalled = recalls_by_set[s]
        correct_positions = sum(1 for i in range(set_size) if recalled[i] == presented[i])
        total_correct += correct_positions
        if correct_positions == set_size:
            absolute_score += set_size
        math_accuracy_errors += math_accuracy_errors_by_set[s]
        math_speed_errors += speed_errors_by_set[s]

    math_total = sum(trials_by_set)
    math_correct = math_total - (math_accuracy_errors + math_speed_errors)
    math_accuracy_rate = math_correct / max(1, math_total)

    return dict(
        ospan_absolute=absolute_score,
        total_correct=total_correct,
        math_errors=math_accuracy_errors + math_speed_errors,
        speed_errors=math_speed_errors,
        accuracy_errors=math_accuracy_errors,
        math_accuracy_rate=math_accuracy_rate,
        math_total=math_total
    )

def save_triallog(trial_rows, path):
    fieldnames = [
        'block_type','set_index','set_size','trial_in_set',
        'problem_text','shown_answer','is_true_display','resp_true','resp_correct','timeout',
        'rt_problem','rt_answer','letter','letter_position','letter_shown','recall_letter','recall_click_index'
    ]
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in trial_rows:
            writer.writerow(row)

def save_summary(summary_dict, path):
    fieldnames = list(summary_dict.keys())
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(summary_dict)

# =========================
# Instructions
# =========================
show_instructions(
    "Welcome!\n\nThis task repeats two steps: (1) quickly solve a math problem, and (2) a letter to remember.\n"
    "After a few of these, you'll select the letters in the exact order they appeared.\n\n"
    "Please work quickly and accurately on the math."
)

# =========================
# Practice 1: Letters only
# =========================
show_instructions(
    "Practice 1: Letter recall\n\nYou'll see a sequence of letters flashing briefly one by one (each 800 ms). "
    "Then you'll click the letters displayed in a matrix in the same order they appeared."
)
letters_prac = random.sample(LETTER_SET, 2)
for L in letters_prac:
    present_letter(L, vis_correct=0, vis_total=0)  # shows 100% when total==0
recall = recall_screen(set_size=2, vis_correct=0, vis_total=0)
correct_positions = sum(1 for i in range(2) if recall[i] == letters_prac[i])
feedback_screen(correct_positions, 2, math_errors_in_set=0)

# =========================
# Practice 2: Math only — estimate pace
# =========================
show_instructions(
    "Practice 2: Math judgment\n\nFirst you'll see a math problem — solve it in your head and click to continue. "
    "Then you'll see a proposed answer — click TRUE or FALSE.\n"
    "We'll use your practice speed to set a reasonable pace for the main task."
)

math_problem_rts = []
math_answer_rts = []
prac_correct = 0
prac_total = 0

for i in range(MATH_PRACTICE_TRIALS):
    prob, correct, shown, is_true = gen_math_problem()
    rt_prob = math_problem_screen(prob, prac_correct, prac_total)

    # no speed limit in practice-2 baseline
    resp_true, rt_ans, _speed_violation = math_answer_screen(
        shown, time_limit=None,
        vis_correct=prac_correct, vis_total=prac_total,
        hard_max_time=HARD_MAX_JUDGEMENT_TIME
    )

    # If hard cap is enabled and hit (resp_true None), treat as incorrect + speed error-like
    if resp_true is None:
        prac_total += 1
    else:
        prac_total += 1
        if resp_true == is_true:
            prac_correct += 1

    math_problem_rts.append(rt_prob)
    math_answer_rts.append(rt_ans if rt_ans is not None else 0.0)

combo_rts = [p + a for p, a in zip(math_problem_rts, math_answer_rts)]
rt_mean = float(np.mean(combo_rts)) if combo_rts else 3.0
rt_sd = float(np.std(combo_rts, ddof=1)) if len(combo_rts) > 1 else 1.0
PERSONAL_TIME_LIMIT = rt_mean + 2.5 * rt_sd

# =========================
# Practice 3: Combined practice (3 sets of size 2)
# =========================
show_instructions(
    "Practice 3: Combined task (math + letters)\n\nNow it all comes together: "
    "math problem → answer judgement → letter display.\n"
    "Speed errors will be recorded if you are slower than your practice pace, "
    "but you will still be allowed to finish the judgement.\n\n"
    "At the end, you'll click the letters displayed in a matrix in the same order they appeared. "
    "You'll do 3 short sets of size 2."
)

combined_practice_sets = [2, 2, 2]

trial_rows = []
set_counter = 0
running_math_correct = 0
running_math_total = 0

for set_size in combined_practice_sets:
    set_counter += 1

    # visible per-set math accuracy
    set_correct = 0
    set_total = 0

    letters_seq = random.sample(LETTER_SET, set_size)
    acc_errors = 0
    speed_errors = 0

    for t in range(set_size):
        prob, correct, shown, is_true = gen_math_problem()
        rt_prob = math_problem_screen(prob, set_correct, set_total)

        time_left = max(0.0, PERSONAL_TIME_LIMIT - rt_prob)

        resp_true, rt_ans, speed_violation = math_answer_screen(
            shown, time_limit=time_left,
            vis_correct=set_correct, vis_total=set_total,
            hard_max_time=HARD_MAX_JUDGEMENT_TIME
        )

        # If hard cap hit: treat as a speed error + incorrect judgement
        if resp_true is None:
            speed_violation = True
            resp_correct = False
        else:
            resp_correct = (resp_true == is_true)

        # record speed error (but do not skip judgement)
        if speed_violation:
            speed_errors += 1

        # count judgement as completed (even if slow)
        set_total += 1
        running_math_total += 1

        if not resp_correct:
            acc_errors += 1
        else:
            set_correct += 1
            running_math_correct += 1

        present_letter(letters_seq[t], set_correct, set_total)

        trial_rows.append(dict(
            block_type='practice_combined', set_index=set_counter,
            set_size=set_size, trial_in_set=t+1,
            problem_text=str(prob), shown_answer=shown, is_true_display=is_true, resp_true=resp_true,
            resp_correct=resp_correct,
            timeout=speed_violation,  # reuse field: now means "speed error"
            rt_problem=rt_prob, rt_answer=rt_ans,
            letter=letters_seq[t], letter_position=t+1, letter_shown=True,
            recall_letter='', recall_click_index=''
        ))

    recalled = recall_screen(set_size, vis_correct=set_correct, vis_total=set_total)
    correct_positions = sum(1 for i in range(set_size) if recalled[i] == letters_seq[i])
    feedback_screen(correct_positions, set_size, acc_errors + speed_errors)

    for i in range(set_size):
        trial_rows.append(dict(
            block_type='practice_combined_recall', set_index=set_counter,
            set_size=set_size, trial_in_set=i+1,
            problem_text='', shown_answer='', is_true_display='', resp_true='',
            resp_correct='', timeout='', rt_problem='', rt_answer='',
            letter=letters_seq[i], letter_position=i+1, letter_shown=False,
            recall_letter=recalled[i] if recalled[i] is not None else '', recall_click_index=i+1
        ))

# =========================
# Main experiment
# =========================
running_math_correct = 0
running_math_total = 0

show_instructions(
    "Main task\n\nYou'll complete combined sets (math problem → answer judgement → letter display).\n\n"
    "Important: Speed errors will be recorded if you are slower than your practice pace, "
    "but you will NOT be skipped past the TRUE/FALSE judgement."
)

all_set_sizes = [s for s in SET_SIZES for _ in range(SETS_PER_SIZE)]
random.shuffle(all_set_sizes)

letters_presented_by_set = []
recalls_by_set = []
trials_by_set = []
math_accuracy_errors_by_set = []
speed_errors_by_set = []

for set_idx, set_size in enumerate(all_set_sizes, start=1):
    set_correct = 0
    set_total = 0

    letters_seq = random.sample(LETTER_SET, set_size)
    acc_errors = 0
    speed_errors = 0

    for t in range(set_size):
        prob, correct, shown, is_true = gen_math_problem()
        rt_prob = math_problem_screen(prob, set_correct, set_total)

        time_left = max(0.0, PERSONAL_TIME_LIMIT - rt_prob)

        resp_true, rt_ans, speed_violation = math_answer_screen(
            shown, time_limit=time_left,
            vis_correct=set_correct, vis_total=set_total,
            hard_max_time=HARD_MAX_JUDGEMENT_TIME
        )

        if resp_true is None:
            speed_violation = True
            resp_correct = False
        else:
            resp_correct = (resp_true == is_true)

        if speed_violation:
            speed_errors += 1

        set_total += 1
        running_math_total += 1

        if not resp_correct:
            acc_errors += 1
        else:
            set_correct += 1
            running_math_correct += 1

        present_letter(letters_seq[t], set_correct, set_total)

        trial_rows.append(dict(
            block_type='main', set_index=set_idx,
            set_size=set_size, trial_in_set=t+1,
            problem_text=str(prob), shown_answer=shown, is_true_display=is_true, resp_true=resp_true,
            resp_correct=resp_correct,
            timeout=speed_violation,  # reuse field: now means "speed error"
            rt_problem=rt_prob, rt_answer=rt_ans,
            letter=letters_seq[t], letter_position=t+1, letter_shown=True,
            recall_letter='', recall_click_index=''
        ))

    recalled = recall_screen(set_size, vis_correct=set_correct, vis_total=set_total)
    correct_positions = sum(1 for i in range(set_size) if recalled[i] == letters_seq[i])
    feedback_screen(correct_positions, set_size, acc_errors + speed_errors)

    letters_presented_by_set.append(letters_seq)
    recalls_by_set.append(recalled)
    trials_by_set.append(set_size)
    math_accuracy_errors_by_set.append(acc_errors)
    speed_errors_by_set.append(speed_errors)

    for i in range(set_size):
        trial_rows.append(dict(
            block_type='main_recall', set_index=set_idx,
            set_size=set_size, trial_in_set=i+1,
            problem_text='', shown_answer='', is_true_display='', resp_true='',
            resp_correct='', timeout='', rt_problem='', rt_answer='',
            letter=letters_seq[i], letter_position=i+1, letter_shown=False,
            recall_letter=recalled[i] if recalled[i] is not None else '', recall_click_index=i+1
        ))

# =========================
# Compute scores and save CSVs
# =========================
summary = compute_scores(
    trials_by_set, letters_presented_by_set, recalls_by_set,
    math_accuracy_errors_by_set, speed_errors_by_set
)
summary.update(dict(
    personal_time_limit=PERSONAL_TIME_LIMIT,
))

save_triallog(trial_rows, triallog_path)
save_summary(summary, summary_path)

show_instructions(
    f"Task complete.\n\n"
    f"OSPAN absolute: {summary['ospan_absolute']}\n"
    f"Total correct (position): {summary['total_correct']}\n"
    f"Math accuracy: {summary['math_accuracy_rate']*100:.1f}%\n"
    f"Speed errors: {summary['speed_errors']}\n"
)

win.close()
core.quit()