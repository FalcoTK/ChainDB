
# ChainDB

**A secure and efficient database solution for your private server, featuring encryption, automatic backups, and dual-node redundancy.**

## Key Features:
- **Rate Limiting**: Built-in protection to limit the number of requests within a defined time window, preventing abuse.
- **Backup System**: Regular automatic backups safeguard your data, with additional backups triggered after any server crash.
- **SHA256-Encrypted JSON**: All data is stored in JSON format and encrypted using the SHA256 algorithm for top-tier security.
- **Dual Node Support**: ChainDB is designed to run multiple server nodes that communicate with each other. If one node fails, the others take over to ensure maximum uptime.
- **Auto Backup on Crash**: Immediately triggers a backup when the server crashes, protecting your valuable data.
- **Web UI & App UI**: ChainDB includes a web-based interface and standalone app support for Linux and Windows.
- **API Support**: Exposes an API for third-party integration. **Important**: Always make sure third-party programs are secure to prevent data breaches.
- **HMAC Authentication**: We use HMAC (Hash-based Message Authentication Code) for secure and reliable API authentication.

## How Dual Node Works:
A **node** in ChainDB refers to a server that handles your database and client requests. When multiple nodes are deployed:
- They communicate continuously to synchronize and share data.
- In the event of a failure, the remaining node(s) will take over operations.
- Each node monitors the others. If a node becomes unresponsive, the remaining nodes assume it has failed and shift workloads to avoid downtime until the failed node is back online.

### Pool Structure:
A **pool** is created when you deploy 3 or more nodes. Inside a pool:
- One node acts as the load balancer, handling incoming requests and managing rate limiting.
- The other nodes handle the database operations, storing and retrieving data.
  
**For efficiency**, you can deploy a 3-node setup:
- **2 nodes for database operations** (storing and retrieving data).
- **1 node dedicated to receiving requests** and managing rate limiting.

This way, if the node responsible for handling requests (called the **probe**) experiences a DDoS attack, the other nodes will shut off the API, ensuring no data is written or read during the attack.

### What is a Probe?
A **probe** is like an API within an API. The probe handles incoming requests from the client and communicates with the other database nodes to write or read data. It ensures that the data is securely managed and can handle tasks like rate limiting and request distribution across the nodes.

### Node and Pool Best Practices:
- **Do not use more than 5 nodes in a single pool.** For best efficiency and cost management, if you require more storage or redundancy, consider creating separate pools with smaller groups of nodes.
- While adding more nodes may improve redundancy, it also increases costs. Use this option only if your use case justifies the expense.

### Enhanced Security:
- When data is written to one node, it is securely replicated and encrypted using the SHA256 algorithm on both nodes.
- This ensures data consistency, security, and redundancy even if one server goes down.

## Security Notice:
When integrating ChainDB with third-party programs, ensure your data remains secure. ChainDB provides secure API access using HMAC authentication, but be sure to review and harden your third-party apps to prevent unauthorized access to sensitive data.


## Planned Future Updates:
- Support for more encryption algorithms like AES.
- Load balancing between nodes for enhanced performance under heavy loads.
- Advanced monitoring and metrics through the web and app UI.

## Documentation & Examples
**Coming soon**—detailed docs and code samples to help you get started quickly.

## Support
If you find this project useful, please consider giving it a ⭐ on GitHub!

