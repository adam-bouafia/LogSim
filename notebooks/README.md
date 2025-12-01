# 📓 LogPress Interactive Notebooks

Interactive Jupyter notebooks for learning and experimenting with LogPress.

## 🚀 Quick Start

### Option 1: Google Colab (No Installation Required)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/adam-bouafia/LogPress/blob/main/notebooks/quickstart.ipynb)

Click the badge above to run the notebook directly in your browser!

### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/adam-bouafia/LogPress.git
cd LogPress/notebooks

# Install dependencies
pip install LogPress jupyter matplotlib seaborn pandas

# Launch Jupyter
jupyter notebook quickstart.ipynb
```

## 📚 Available Notebooks

### `quickstart.ipynb` - Complete Interactive Tutorial

**What you'll learn:**
- ⚡ Compress logs in 2 lines of code
- 🔍 Query compressed logs without decompression
- 📊 Extract and visualize log schemas
- 🎯 Compare query performance (compressed vs uncompressed)
- 📈 View real-world benchmark results

**Duration:** ~10-15 minutes

**Topics covered:**
1. Installation and setup
2. Basic compression (your first 2 lines)
3. Querying compressed logs
4. Schema extraction
5. Compression performance visualization
6. Query speedup benchmarks
7. Template distribution analysis
8. Real-world performance metrics

**Visualizations included:**
- 📊 Compression ratio charts
- ⚡ Query performance comparison
- 📈 Template distribution heatmaps
- 💾 Storage savings by dataset

## 🎯 Learning Path

**New to LogPress?** Start here:
1. Run `quickstart.ipynb` (this notebook)
2. Read [docs/quickstart.md](../docs/quickstart.md)
3. Explore [examples/](../examples/)
4. Check [docs/api_reference.md](../docs/api_reference.md)

**Want production integration?**
- See [docs/integration_guide.md](../docs/integration_guide.md) for Flask, FastAPI, Docker, Kubernetes
- Check [examples/07_flask_api.py](../examples/07_flask_api.py) for REST API
- See [examples/08_fastapi_service.py](../examples/08_fastapi_service.py) for async microservice

## 🔧 Requirements

```bash
pip install LogPress matplotlib seaborn pandas jupyter
```

Or with notebook support:

```bash
pip install "LogPress[notebooks]"
```

## 📊 What to Expect

### Performance Metrics (from research paper)

| Dataset | Log Entries | Compression Ratio | Schema Accuracy | Query Speedup |
|---------|------------|-------------------|-----------------|---------------|
| Apache | 52K | 11.1× | 92.3% | 6.2× |
| HealthApp | 212K | 13.0× | 94.5% | 7.1× |
| Zookeeper | 74K | 11.5× | 93.1% | 6.5× |
| OpenStack | 137K | 11.8× | 94.2% | 6.8× |
| Proxifier | 21K | 11.7× | 93.8% | 5.9× |
| **Average** | **99K** | **12.2×** | **93.7%** | **6.5×** |

### Sample Visualizations

The notebook generates:
- **Compression charts**: See how compression ratio scales with file size
- **Query benchmarks**: Compare indexed vs grep-style searches
- **Schema distribution**: Visualize which log patterns are most common
- **Storage savings**: Before/after file size comparisons

## 🤝 Contributing

Have ideas for new notebooks? Found a bug? Contributions welcome!

1. Fork the repository
2. Create your notebook in `notebooks/`
3. Add entry to this README
4. Submit a pull request

## 📝 License

MIT License - see [LICENSE](../LICENSE) for details

## 🔗 Links

- **PyPI**: [https://pypi.org/project/LogPress/](https://pypi.org/project/LogPress/)
- **GitHub**: [adam-bouafia/LogPress](https://github.com/adam-bouafia/LogPress)
- **Documentation**: [docs/](../docs/)
- **Examples**: [examples/](../examples/)

---

💡 **Tip**: Run the notebook in Google Colab for instant access without any setup!
