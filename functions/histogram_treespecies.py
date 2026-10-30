import rasterio
import numpy as np
import matplotlib.pyplot as plt


def histogram_treespecies(tif_path):
    mapping = {0: "pine", 1: "spruce", 2: "douglas fir", 3: "larch", 4: "fir", 5: "beech", 6: "oak", 7: "birch",
               8: "alder", 9: "other deciduous", 800: "uncertain"}

    with rasterio.open(tif_path) as src:
        # Instantly get unique pixel values and their counts
        vals, counts = np.unique(src.read(1), return_counts=True)

    # Filter out nodata and map to names in one quick step
    valid_data = {mapping[v]: c for v, c in zip(vals, counts) if v in mapping}

    # Plot
    plt.bar(valid_data.keys(), valid_data.values())
    plt.xticks(rotation=45)
    plt.title("Occurence of tree species in the AOI (by pixel) (all trees)")
    plt.show()