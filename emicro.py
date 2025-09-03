import os
import time
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

# === GEMINI API SETUP ===
genai.configure(api_key="your_api_key")
model = genai.GenerativeModel("gemini-1.5-flash")

def get_gemini_answer(question, options):
    """Ask Gemini which option is most correct"""
    prompt = f"""
    You are answering multiple-choice questions.
    Question: {question}
    Options:
    {chr(10).join([f"{i+1}. {opt}" for i, opt in enumerate(options)])}
    Respond with ONLY the number of the correct option (1, 2, 3, ...).
    """
    try:
        response = model.generate_content(prompt)
        answer_text = response.text.strip()
        print(f"Gemini Response: {answer_text}")
        # Extract first number Gemini gives
        for i in range(len(options)):
            if str(i+1) in answer_text:
                return i
        return 0  # fallback to first option
    except Exception as e:
        print("Gemini error:", e)
        return 0

# === SELENIUM SETUP ===
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# === LIST OF MODULE LINKS ===
module_links =[ "https://learn.microsoft.com/en-us/training/modules/prepare-azure-ai-development/1-introduction",
                "https://learn.microsoft.com/en-us/training/modules/explore-models-azure-ai-studio/1-introduction",
                "https://learn.microsoft.com/en-us/training/modules/ai-foundry-sdk/01-introduction",
                "https://learn.microsoft.com/en-us/training/modules/get-started-prompt-flow-ai-studio/1-introduction",
                "https://learn.microsoft.com/en-us/training/modules/build-copilot-ai-studio/1-introduction",
                "https://learn.microsoft.com/en-us/training/modules/finetune-model-copilot-ai-studio/1-introduction",
                "https://learn.microsoft.com/en-us/training/modules/responsible-ai-studio/1-introduction",
                "https://learn.microsoft.com/en-us/training/modules/evaluate-models-azure-ai-studio/1-introduction",
                "https://learn.microsoft.com/en-us/training/modules/ai-agent-fundamentals/1-introduction",
                "https://learn.microsoft.com/en-us/training/modules/develop-ai-agent-azure/1-introduction",
                "https://learn.microsoft.com/en-us/training/modules/build-agent-with-custom-tools/1-introduction",
                "https://learn.microsoft.com/en-us/training/modules/develop-multi-agent-azure-ai-foundry/1-introduction",
                "https://learn.microsoft.com/en-us/training/modules/connect-agent-to-mcp-tools/1-introduction",
                "https://learn.microsoft.com/en-us/training/modules/develop-ai-agent-with-semantic-kernel/1-introduction",
                "https://learn.microsoft.com/en-us/training/modules/orchestrate-semantic-kernel-multi-agent-solution/1-introduction"
               
]

# === FUNCTION TO PROCESS A SINGLE LINK ===
def process_module(url, wait_time):
    driver.get(url)
    print(f"\nOpened module: {url}")
    time.sleep(wait_time)  # Custom wait time for login or loading

    while True:
        time.sleep(2)
        print("Scanning page...")

        # === CHECK FOR MCQs ===
        try:
            questions = driver.find_elements(By.CSS_SELECTOR, "div.quiz-question")
            if questions:
                for q in questions:
                    question_text = q.find_element(By.CSS_SELECTOR, "div.field-label p").text.strip()
                    options = q.find_elements(By.CSS_SELECTOR, "label.quiz-choice p")
                    option_texts = [opt.text.strip() for opt in options]

                    # Get Gemini answer
                    ans_index = get_gemini_answer(question_text, option_texts)

                    # Select the answer
                    radio_inputs = q.find_elements(By.CSS_SELECTOR, "input.choice-input")
                    radio_inputs[ans_index].click()
                    time.sleep(1)

                # === CLICK SUBMIT BUTTON AFTER SELECTING ANSWERS ===
                try:
                    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[data-bi-name='module-unit-module-assessment-submit']")
                    submit_btn.click()
                    print("Submitted answers ✅")
                    time.sleep(2)
                except NoSuchElementException:
                    print("No Submit button found.")
        except NoSuchElementException:
            pass

        # === CHECK FOR FINISH BUTTON ===
        try:
            finish_button = driver.find_element(By.XPATH, "//a[contains(text(),'Go back to finish')]")
            print("Reached Finish Page. Moving to next module.")
            break
        except NoSuchElementException:
            pass

        # === CLICK NEXT BUTTON ===
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            next_button = driver.find_element(By.CSS_SELECTOR, "a.button.button-primary.button-filled[data-bi-name='continue']")
            next_button.click()
            print("Clicked Next...")
            time.sleep(3)
        except (NoSuchElementException, ElementClickInterceptedException):
            print("No Next button found. Possibly end of module.")
            break

# === MAIN LOOP FOR ALL LINKS ===
for i, link in enumerate(module_links):
    wait_time = 100 if i == 0 else 10  # First link gets 40 sec, others 10 sec
    process_module(link, wait_time)

driver.quit()
print("All modules completed ✅")

