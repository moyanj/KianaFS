# KianaFS

![GitHub](https://img.shields.io/github/license/moyanj/kianafs)
![Database](https://img.shields.io/badge/database-PostgreSQL-blue)

<p align="center">
    <a href="README.md">English</a> &nbsp;&bull;&nbsp;
    <a>中文</a>
</p>

KianaFS是一款智能轻量级分布式存储系统，兼具高性能与易用性。

## 功能特性

- **虚拟文件系统** - 将异构存储映射为统一目录树结构，简化文件管理。
- **异构存储统一接入** - 通过适配器模式集成多种存储协议，支持无缝切换存储后端。
- **高可用性**: 通过冗余存储和故障转移机制，确保数据的持续可用性，避免单点故障。
- **分布式存储**: 数据分布在多个节点上，提升存储容量和可用性，支持大规模数据存储需求。
- **高可扩展性**: 支持多种存储后端，满足不同场景的需求，从本地存储到云端存储均可轻松扩展。
- **跨平台访问**: 提供RESTful API、CLI工具和Web管理界面（开发中），支持多终端操作。
- **容器化部署**: 提供Docker镜像和Kubernetes部署方案，简化部署流程，提升运维效率。

### 驱动支持
- [x] 本地磁盘
- [x] AList V3
- [x] Amazon S3
- [ ] WebDAV
- [x] FTP
- [ ] SMB
- [ ] SSH
- [ ] HTTP API

## 架构设计

![export.jpeg](https://s2.loli.net/2025/03/08/DIjrNf3WRTF9uwP.jpg)

KianaFS采用模块化设计，核心模块负责文件系统的逻辑处理，存储驱动层通过适配器模式支持多种存储后端，元数据库用于存储文件系统的元数据，确保数据的一致性和可靠性。

## 快速配置

(编写中)

我们正在完善快速配置文档，帮助用户快速上手KianaFS。预计将在下一版本中提供详细的配置指南。

## 技术栈

- **核心框架**：FastAPI, Tortoise ORM
- **数据库**：MySQL, PostgreSQL, SQLite, SQL Server
- **容器化**：Docker, Kubernetes
- **开发工具**：Black, pyright
- **文档生成**：MkDocs

KianaFS采用现代化的技术栈，确保系统的高性能和易维护性。FastAPI提供高效的API服务，Tortoise ORM简化数据库操作，Docker和Kubernetes支持容器化部署，提升系统的可移植性和扩展性。

## 参与贡献

我们欢迎社区成员积极参与KianaFS的开发与维护！以下是参与贡献的步骤：

1. Fork仓库并创建特性分支。
2. 提交代码，确保代码风格一致，并通过单元测试。
3. 创建Pull Request，详细描述你的修改内容和动机。

## 许可证

KianaFS遵循MIT许可证。你可以自由使用、修改和分发KianaFS，但需保留版权声明和许可证信息。

## 联系我们

- **问题追踪**: [GitHub Issues](https://github.com/moyanj/kianafs/issues)
- **讨论区**: [GitHub Discussions](https://github.com/moyanj/kianafs/discussions)
- **邮件支持**: kianafs@moyanjdc.top
- **社交媒体**: [@KianaFS](https://twitter.com/KianaFS)

如果你有任何问题、建议或反馈，欢迎随时联系我们！