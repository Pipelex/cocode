# My Project ⚡️

*Replace "My Project" with your actual project name*

### Use this template

This is a template repository: don't clone it, click the green `Use this template` button at the top-right of the Github repo page.
Once you've created your repository from it, then you can clone it and follow the instructions below:

**Next steps after creating from template** (or later when you feel like it)
1. In `pyproject.toml`, replace "my-project" with your project name in the header, then replace "my_project" with your package name (using underscores) in the "packages" parameter of [tool.mypy] and the "include" parameter of [tool.pyright]
2. Replace "my_project" directory name with your package name (use underscores)
3. Update this README.md with your project details
4. Update the package imports in your code as needed

---

### Create virtual environment, install Pipelex and other dependencies

```bash
make install
```

This will install the Pipelex python library and its dependencies using uv.

### Set up environment variables

```bash
cp .env.example .env
```

Enter your API keys into your `.env` file. The `OPENAI_API_KEY` is enough to get you started, but some pipelines require models from other providers.

---

## Contact & Support

| Channel                                | Use case                                                                  |
| -------------------------------------- | ------------------------------------------------------------------------- |
| **GitHub Discussions → "Show & Tell"** | Share ideas, brainstorm, get early feedback.                              |
| **GitHub Issues**                      | Report bugs or request features.                                          |
| **Email (privacy & security)**         | [security@pipelex.com](mailto:security@pipelex.com)                       |
| **Discord**                            | Real-time chat — [https://go.pipelex.com/discord](https://go.pipelex.com/discord) |


## 📝 License

This project is licensed under the [MIT license](LICENSE). Runtime dependencies are distributed under their own licenses via PyPI.

---

*Happy piping!* 🚀
