# 安全与联系

## 联系创始人

如需讨论**设计合作、集成、研究协作或产品问题**，可直接联系 **Chris Shi**：

- 邮箱：[shi275773124@gmail.com](mailto:shi275773124@gmail.com?subject=Falsify%20inquiry)
- X / Twitter：[https://x.com/aishikejian](https://x.com/aishikejian)
- GitHub：[https://github.com/shi275773124/Falsify](https://github.com/shi275773124/Falsify)

Falsify 是开源核心、以本地/BYOK 为主的工具链；这个联系入口不代表已提供托管服务、代运维部署或私有基础设施。

## 安全边界

Falsify 是本地/BYOK 工具链。任何审查输入和生成的回执都可能包含代码、运行细节、来源链接或 provider 输出，应按敏感信息处理。

- 将 provider 密钥保存在环境变量或 GitHub Secrets 中，绝不提交。
- 审查发送给模型 provider 的文件范围；CLI 本身不能让第三方 provider 自动变成私有。
- 将 JSON/Markdown 回执保存在符合仓库与留存策略的位置。
- PASS 不是部署、合并、交易或执行生产操作的授权；它只是限定范围内的证据判定。

本地 Web Console 默认绑定在 127.0.0.1。在审查 provider 配置和网络边界前，不要将它暴露到本机以外。

## 报告安全问题

**请不要在公开 issue 中披露漏洞细节、凭证、私有回执或可被滥用的复现步骤。** 请发送邮件至 [shi275773124@gmail.com](mailto:shi275773124@gmail.com?subject=Falsify%20security%20report)，主题使用 Falsify security report。请说明受影响版本或 commit、最小复现、影响与前置条件，并标注哪些材料必须私下处理。

## 产品问题与公开贡献

公开 bug、文档修正和模板改进可以提交 GitHub issue；请附上命令、预期行为、实际行为和已脱敏的材料。任何能力声明应指向可复现命令、源文件或测试；本项目不将营销文案视为证据。
