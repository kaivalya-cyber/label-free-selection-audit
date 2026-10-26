"""Print parquet footer metadata (row groups + per-column compressed sizes) via ranged read."""

import sys

import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem


def main(repo, path):
    fs = HfFileSystem()
    with fs.open(f"datasets/{repo}/{path}", "rb") as f:
        pf = pq.ParquetFile(f)
        md = pf.metadata
        print(f"# {repo}/{path}")
        print(f"rows={md.num_rows} row_groups={md.num_row_groups} size={fs.info(f'datasets/{repo}/{path}')['size']:,} bytes")
        per_col = {}
        for rg in range(md.num_row_groups):
            g = md.row_group(rg)
            for c in range(g.num_columns):
                col = g.column(c)
                per_col[col.path_in_schema] = per_col.get(col.path_in_schema, 0) + col.total_compressed_size
        tot = sum(per_col.values())
        for k, v in sorted(per_col.items(), key=lambda kv: -kv[1]):
            print(f"  {v/1e6:9.1f} MB  {100*v/tot:5.1f}%  {k}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
