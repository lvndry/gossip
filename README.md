# Gossip Assistant

## Prerequisites

- Python 3.12 + uv
- Node.js 22
- Qdrant API Key
- OpenAI API Key
- Linkup API Key

## Build dataset

You can build the dataset by either:

```bash
POST /process-articles
```

or

```sh
cd apps/backend
uv run python -m src.embed
```

**⚠️ NOTE**: backend server should not be running when building the dataset

## Quick start

```sh
cd apps/backend
uv sync
cd -
cd apps/frontend
npm install
cd -
./dev.sh
```

This will start the backend and the frontend servers.


## Implementation details

**Backend**

At first wanted to use Linkup deep research to build the dataset but couldn't figure out how to get satisfying results. Only got 3-5 articles per query.
So I ended up using RSS sources from vsd and public and get the articles from there. Still I used Linkup fetch function to get the articles.

I used Qdrant as vector database as it allowed to easily create a local db
I used OpenAI as embedding model.

For the chunking I went for something super simple and basic just for this example. In a real production use case I'd use a more advanced chunking strategy with seperators.

**Frontend**

I used Next.js with React and TailwindCSS for the frontend.
I went for ai sdk from vercel as it's pretty straightforward to use
