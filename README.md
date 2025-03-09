# KianaFS

![GitHub](https://img.shields.io/github/license/moyan/kianafs)
![Database](https://img.shields.io/badge/database-PostgreSQL-blue)

<p align="center">
    <a>English</a> &nbsp;&bull;&nbsp;
    <a href="README_zh.md">中文</a>
</p>

KianaFS is a lightweight, high-performance distributed storage system designed for ease of use.

## Features

- **Virtual File System**: Maps heterogeneous storage into a unified directory structure.
- **Unified Storage Access**: Supports multiple storage protocols via adapters.
- **High Availability**: Redundant storage and failover mechanisms.
- **Distributed Storage**: Data spread across nodes for scalability.
- **Cross-Platform Access**: RESTful API, CLI tools, and web interface (in development).
- **Containerized Deployment**: Docker and Kubernetes support.

### Supported Drivers
- [x] Local Disk
- [x] AList V3
- [x] Amazon S3
- [ ] WebDAV
- [x] FTP
- [ ] SMB
- [ ] SSH
- [ ] HTTP API

## Architecture

![export.jpeg](https://s2.loli.net/2025/03/08/DIjrNf3WRTF9uwP.jpg)

KianaFS uses a modular design with a core module for file system logic, a storage driver layer for backend integration, and a metadata database for consistency.

## Quick Setup

(Under Development)

## Tech Stack

- **Core**: FastAPI, Tortoise ORM
- **Database**: MySQL, PostgreSQL, SQLite, SQL Server
- **Containerization**: Docker, Kubernetes
- **Tools**: Black, pyright, MkDocs

## Contributing

1. Fork the repo and create a feature branch.
2. Submit code with consistent style and passing tests.
3. Open a Pull Request with clear details.

## License

MIT License.

## Contact

- **Issues**: [GitHub Issues](https://github.com/moyanj/kianafs/issues)
- **Discussions**: [GitHub Discussions](https://github.com/moyanj/kianafs/discussions)
- **Email**: kianafs@moyanjdc.top
- **Twitter**: [@KianaFS](https://twitter.com/KianaFS)

For questions or feedback, reach out anytime!