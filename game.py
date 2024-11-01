import requests
import math


def load_words():
    response = requests.get('https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt')
    words = response.text.split()
    five_letter_words = [word.lower() for word in words if len(word) == 5]
    # 确保包含目标单词
    if 'theft' not in five_letter_words:
        five_letter_words.append('theft')
    return five_letter_words

# 计算每个猜测单词的熵
def calculate_entropy(possible_answers):
    entropy_dict = {}
    total = len(possible_answers)
    for guess in possible_answers:
        pattern_counts = {}
        for actual in possible_answers:
            pattern = get_feedback_pattern(guess, actual)
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        entropy = 0
        for count in pattern_counts.values():
            p = count / total
            entropy -= p * math.log2(p)
        entropy_dict[guess] = entropy
    return entropy_dict

# 获取反馈模式，例如 "correct-absent-present-correct-absent"
def get_feedback_pattern(guess, actual):
    feedback = ['absent'] * 5
    actual_letters = list(actual)
    # 处理correct（位置正确）
    for i in range(5):
        if guess[i] == actual[i]:
            feedback[i] = 'correct'
            actual_letters[i] = None
    # 处理present（字母存在但位置不对）
    for i in range(5):
        if feedback[i] == 'absent' and guess[i] in actual_letters:
            feedback[i] = 'present'
            actual_letters[actual_letters.index(guess[i])] = None
    return '-'.join(feedback)

# 根据反馈更新可能的答案列表
def update_possible_answers(possible_answers, guess, feedback):
    new_possible_answers = []
    for word in possible_answers:
        if get_feedback_pattern(guess, word) == feedback:
            new_possible_answers.append(word)
    return new_possible_answers

def main():
    # 加载五字母单词列表
    possible_answers = load_words()
    attempts = 6
    seed = input("please in put seed value (optional, press Enter to skip):")
    if not seed:
        seed = '1234'  # 默认种子
    for attempt in range(attempts):
        # 计算熵，选择熵最大的单词作为猜测
        entropy_dict = calculate_entropy(possible_answers)
        guess = max(entropy_dict, key=entropy_dict.get)
        print(f"\n第 {attempt + 1} 次尝试：{guess}")

        # 调用API获取反馈
        response = requests.get(
            'https://wordle.votee.dev:8000/random',
            params={'guess': guess, 'seed': seed}
        )
        if response.status_code != 200:
            print("API请求失败，请检查网络连接或API地址。")
            break
        feedback_list = response.json()
        print(f"反馈：{feedback_list}")

        # 解析反馈
        feedback = '-'.join([item['result'] for item in feedback_list])

        if all(item['result'] == 'correct' for item in feedback_list):
            print(f"恭喜！你找到了正确的单词：{guess}")
            break
        else:
            possible_answers = update_possible_answers(possible_answers, guess, feedback)
            if not possible_answers:
                print("没有符合条件的单词，可能是反馈有误。")
                break
    else:
        print("在6次尝试内未能找到单词。")

if __name__ == "__main__":
    main()