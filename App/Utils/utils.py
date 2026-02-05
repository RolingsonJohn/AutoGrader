import os
import configparser
import matplotlib.pyplot as plt
import zipfile

def files_extraction(src_path:str, dst_path:str):
    """
    """

    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    try:
        with zipfile.ZipFile(src_path, 'r') as zip_ref:
            zip_ref.extractall(dst_path)
    except Exception as e:
        print(e)


def load_files(src_path:str) -> dict:
    directory_files = {}
    for subdirectory in os.listdir(src_path):
        directory = f"{src_path}/{subdirectory}"
        directory_files.update({subdirectory : [f"{directory}/{file}" for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]})
    return directory_files

def plot(xdata: list, ydata: list, xlabel: str, ylabel: str, title: str, output: str):
    plt.figure(figsize=(10, 6))
    plt.plot(xdata, ydata, color='skyblue', alpha=0.5, linewidth=2)
    plt.scatter(xdata, ydata, color='blue', zorder=5)
    plt.xlabel(xlabel=xlabel)
    plt.ylabel(ylabel=ylabel)
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output)
    #plt.show()

def boxplot(xdata: list, xlabels: list, xlabel: str, ylabel: str, title: str, output: str):
    plt.figure(figsize=(10, 6))
    plt.boxplot(xdata, patch_artist=True)
    plt.xticks(ticks=range(1, len(xlabels) + 1), labels=xlabels, rotation=45, ha='right')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output)
    plt.close()