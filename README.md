# Customer Retention System for Telecom Industry
*Proactively reduce customer churn with AI-driven personalized offers*

---

## Description
The **Customer Retention System** is an end-to-end solution designed for the telecom industry to **retain high-value customers** by detecting churn risk and delivering tailored offers. Inspired by research showing that retaining existing customers is far less costly than acquiring new ones, this project combines:

- **User-facing chatbot** (Rasa) for handling FAQs and basic support
- **Churn prediction** (Linear Regression on IBM Telco dataset)
- **AI-powered offer generation** (Agno agent)
- **Interactive visualizations** (Tableau dashboard)
- **Topic modeling** (NMF on chat logs)

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

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

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