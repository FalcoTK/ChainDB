

# ChainDB 🚀

**A secure and efficient database solution for your private server, featuring encryption, automatic backups, and dual-node redundancy.**

## 🌟 Key Features:
- **🛡️ Rate Limiting**: Built-in protection to limit the number of requests within a defined time window, preventing abuse.
- **🔄 Backup System**: Regular automatic backups safeguard your data, with additional backups triggered after any server crash.
- **🔐 SHA256-Encrypted JSON**: All data is stored in JSON format and encrypted using the SHA256 algorithm for top-tier security.
- **🖥️ Dual Node Support**: ChainDB is designed to run multiple server nodes that communicate with each other. If one node fails, the others take over to ensure maximum uptime.
- **⚠️ Auto Backup on Crash**: Immediately triggers a backup when the server crashes, protecting your valuable data.
- **🌐 Web UI & 🖥️ App UI**: ChainDB includes a web-based interface and standalone app support for Linux and Windows.
- **📡 API Support**: Exposes an API for third-party integration. **Important**: Always make sure third-party programs are secure to prevent data breaches!

## 🔧 How Dual Node Works:
A **node** in ChainDB refers to a server that handles your database and client requests. When multiple nodes are deployed:
- They communicate continuously to synchronize and share data.
- In the event of a failure, the remaining node(s) will take over operations.
- Each node monitors the others. If a node becomes unresponsive, the remaining nodes assume it has failed and shift workloads to avoid downtime until the failed node is back online.

### 🔒 Enhanced Security:
- When data is written to one node, it is securely replicated and encrypted using the SHA256 algorithm on both nodes.
- This ensures data consistency, security, and redundancy even if one server goes down.

## 🛠️ Installation Instructions:
1. Clone the ChainDB repository from the GitHub link.
2. Install dependencies (mention the required dependencies).
3. Configure the environment for dual-node support, rate limiting, backup schedules, and encryption keys.
4. Deploy either the web UI or the desktop app based on your needs.


## ⚠️ Security Notice:
When integrating ChainDB with third-party programs, ensure your data remains secure. ChainDB provides secure API access, but be sure to review and harden your third-party apps to prevent unauthorized access to sensitive data.


## 🔮 Planned Future Updates:
- 🔑 Support for more encryption algorithms like AES.
- ⚖️ Load balancing between nodes for enhanced performance under heavy loads.
- 📊 Advanced monitoring and metrics through the web and app UI.
