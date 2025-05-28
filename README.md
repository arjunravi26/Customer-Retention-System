# Customer Retention System for Telecom Industry
*Proactively reduce customer churn with AI-driven personalized offers*

---

## Description

Customer churn in telecom can erode revenue and escalate acquisition costs if not addressed early. This project delivers a compact, end-to-end retention toolkit that:

- **Detects churn risk** ahead of time with a Linear Regression model trained on the IBM Telco dataset.
- **Automates personalized offers** via an Agno AI agent that pulls a customer’s data, churn score and available promotions to craft and send tailored emails.
- **Visualizes customer insights** in a Tableau dashboard—demographics, usage patterns, churn trends—so admins spot issues and opportunities at a glance.
- **Surfaces common pain points** through NMF topic modeling on Rasa chatbot logs, helps to identify customer need and problems.
- **Helps customers** directly with a Rasa chatbot for quick answers about service issues and know about offers.

Together, these components turn raw data into proactive retention actions—keeping customers engaged before they consider leaving.


---

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Contributing](#contributing)
4. [License](#license)
5. [Contact Information](#contact-information)
6. [Acknowledgments](#acknowledgments)

---

## Installation

### Prerequisites
- Python 3.8+
- Git
- Docker
### Clone the Repository
```bash
git clone https://github.com/arjunravi26/Customer-Retention-System.git
cd Customer-Retention-System
````

### Create & Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Rasa Setup

```bash
cd rasa_chatbot
rasa train
rasa run --enable-api
```

---

## Usage

### To run service(containers)

```bash
docker-compose up --build
```

---

## Contributing

Contributions are welcome! To get started:

1. Fork the repo
2. Create a new branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to your branch: `git push origin feature/YourFeature`
5. Open a Pull Request and describe your improvements.

---

## License

This project is licensed under the **GNU GENERAL PUBLIC LICENSE**. See [LICENSE](LICENSE) for details.

---

## Contact Information

* **GitHub:** [@arjunravi26](https://github.com/arjunravi26)
* **Linkedln:** [Arjun Ravi](https://www.linkedin.com/in/arjun-ravi-60215330b/)

---

## Acknowledgments

* **IBM** for the Telco Customer Churn dataset
* **Rasa** for the open-source chatbot framework
* **Agno AI** for agent orchestration
* **Tableau** for data visualization tools
* Research insights from **Harvard Business Review** on customer retention