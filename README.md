# 🌍 Autonomous Multi-Agent Travel Planner

A production-grade **Multi-Agent System (MAS)** built with the **BeeAI Framework** and **IBM watsonx.ai**. This project orchestrates a team of four specialized AI agents to autonomously research, plan, and synthesize complex travel itineraries with human-in-the-loop validation.

## 🚀 Overview

This application moves beyond simple chatbots by simulating a professional travel agency. A central **Travel Coordinator** analyzes user requests and intelligently delegates sub-tasks to domain experts (Weather, Culture, and Destination Research). The system utilizes **HandoffTools** to maintain context across agents and implements strict **security requirements** to validate external tool usage.

## ✨ Key Features

  * **🤖 Hub-and-Spoke Architecture:** A central coordinator agent manages three specialized sub-agents, delegating tasks based on expertise.
  * **🔄 Intelligent Handoffs:** Uses `HandoffTool` to transfer conversation context and task execution seamlessly between agents.
  * **🛡️ Human-in-the-Loop Security:** Implements `AskPermissionRequirement` to intercept sensitive actions (like external API calls) and require explicit user approval.
  * **🧠 Chain-of-Thought Reasoning:** Enforces `ThinkTool` usage via `ConditionalRequirement`, ensuring agents "plan" their actions before execution.
  * **🌦️ Real-Time Integration:** Fetches live weather data (`OpenMeteoTool`) and factual context (`WikipediaTool`).

## 👥 The Agent Team

The system is composed of four distinct agents, each with a specific role and toolset:

| Agent Role | Responsibility | Tools Used |
| :--- | :--- | :--- |
| **Travel Coordinator** | **Primary Interface.** Strategies, delegates tasks, and synthesizes final plans. | `HandoffTool`, `ThinkTool` |
| **Destination Expert** | Researches landmarks, history, and safety advisories. | `WikipediaTool`, `ThinkTool` |
| **Meteorologist** | Analyzes climate patterns and recommends packing gear. | `OpenMeteoTool`, `ThinkTool` |
| **Cultural Expert** | Advises on etiquette, language tips, and local customs. | `WikipediaTool`, `ThinkTool` |

## 🛠️ Tech Stack

  * **Framework:** [BeeAI Framework](https://github.com/i-am-bee/beeai-framework)
  * **LLM Provider:** IBM watsonx.ai
  * **Model:** `meta-llama/llama-4-maverick-17b-128e-instruct-fp8` (Configurable)
  * **Language:** Python 3.10+

## ⚙️ Installation

1.  **Clone the repository**

    ```bash
    git clone https://github.com/yourusername/agentic-travel-planner.git
    cd agentic-travel-planner
    ```

2.  **Install dependencies**

    ```bash
    pip install beeai-framework pydantic python-dotenv
    ```

3.  **Set up Environment Variables**
    Create a `.env` file in the root directory with your IBM watsonx credentials:

    ```env
    WATSONX_API_KEY=your_ibm_api_key
    WATSONX_PROJECT_ID=your_project_id
    WATSONX_URL=https://us-south.ml.cloud.ibm.com
    ```

## 🏃 Usage

Run the main script to launch the agent team:

```bash
python t12.py
```

### Example Workflow

The system is pre-configured with a complex scenario:

> *"I'm planning a 2-week cultural immersion trip to Japan (Tokyo and Osaka)... What should I know about the destination, weather expectations, and language/cultural tips?"*

1.  **Coordinator** receives the prompt and plans a strategy.
2.  **Coordinator** invokes `HandoffTool` to call the **Destination Expert**.
3.  **Security Check:** The system pauses and asks the user for permission to proceed.
4.  **Destination Expert** researches Tokyo/Osaka via Wikipedia and returns insights.
5.  **Coordinator** repeats the process for Weather and Culture agents.
6.  **Final Output:** A synthesized, comprehensive travel guide.

## 📂 Project Structure

```text
├── t12.py                  # Main application entry point (Agent definitions)
├── requirements.txt        # Python dependencies
├── .env                    # API credentials (excluded from git)
└── README.md               # Project documentation
```

## 🤝 Contributing

Contributions are welcome\! Please open an issue or submit a pull request if you'd like to add new tools (e.g., Flight Search, Hotel Booking) or new agent personas.

