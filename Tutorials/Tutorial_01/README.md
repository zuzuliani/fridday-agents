# Tutorial 1: Introduction to LangChain

Welcome to the first tutorial in our LangChain and LangGraph series! In this tutorial, we'll introduce you to LangChain, a powerful framework for building applications with large language models (LLMs).

## What you'll learn

1. What is LangChain and why it's useful
2. How to install and set up LangChain
3. Basic concepts: Chains, Agents, and Memory
4. Building your first LangChain application

## Prerequisites

- Basic understanding of Python (3.8 or higher)
- Familiarity with Jupyter Notebooks
- Git installed on your system
- A Groq API key (sign up at https://console.groq.com)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/rahulsamant37/langchain-langgraph-starter
cd langchain-langgraph-starter
```

### 2. Create and Activate Virtual Environment

#### For Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
cd Tutorial_01
```

#### For Windows:
```cmd
python -m venv venv
.\venv\Scripts\activate
cd Tutorial_01
```

### 3. Install Required Packages

```bash
pip install -r ../requirements.txt
```

### 4. Set Up API Keys

#### For Linux/macOS:
```bash
export GROQ_API_KEY='your-api-key-here'
cp ../.env.example ../.env
```

#### For Windows:
```cmd
set GROQ_API_KEY=your-api-key-here
copy ..\.env.example ..\.env
```

Edit the `.env` file and update these values:
```plaintext
GROQ_API_KEY=your-api-key-here
LANGSMITH_API_KEY=your-langsmith-key-here  # Optional for tracking LLM calls
```

### 5. Launch Jupyter Notebook

```bash
jupyter notebook Tutorial_01_Introduction_to_LangChain.ipynb
```

### 6. Follow the Tutorial

The notebook will guide you through:
- Setting up your first LangChain environment
- Understanding core LangChain concepts
- Creating a simple chat application
- Working with different LLM providers
- Implementing basic memory systems

## Troubleshooting

### Common Issues

1. **Virtual Environment Not Activating**
   - Windows: Ensure PowerShell execution policy allows script execution
   - Linux/macOS: Check Python3 installation and permissions

2. **Package Installation Errors**
   - Upgrade pip: `python -m pip install --upgrade pip`
   - Install wheel: `pip install wheel`
   - For Windows: Install Visual C++ Build Tools if required

3. **API Key Issues**
   - Verify key format in .env file
   - Restart Jupyter kernel after setting environment variables
   - Check for spaces or quotes in the API key string

## Next Steps

After completing this tutorial:
1. Explore the advanced concepts in Tutorial 2
2. Practice building simple chains and agents
3. Review the LangChain documentation for additional features
4. Join the LangChain Discord community for support

Stay tuned for Tutorial 2 where we'll dive deeper into:
- Advanced LangChain patterns
- Custom chain development
- Integration with vector databases
- Practical use cases and deployment strategies

## Additional Resources

- Official LangChain Documentation
- Groq API Documentation
- LangSmith Documentation (for monitoring)
- Community Forums and Support Channels

Happy learning!