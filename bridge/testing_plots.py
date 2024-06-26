import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os


def draw_wavy_break(ax, position, wavy_width, wavy_height):
    x = np.linspace(-wavy_width, wavy_width, 100)
    y = np.sin(3*x/wavy_width) * wavy_height + position
    ax.plot(x, y, transform=ax.get_yaxis_transform(), color='k', clip_on=False)

data_path = "/home/marcelr/rlds_dataset_builder/data"
# Load data from JSON files
with open(os.path.join(data_path, 'lupus_tasks_clean.json')) as file:
    tasks_data = json.load(file)['counter_data']
with open(os.path.join(data_path, 'normalized_lupus_objects.json')) as file:
    objects_data = json.load(file)['counter_data']
with open(os.path.join(data_path, 'normalized_lupus_spatial_relations.json')) as file:
    spatial_data = json.load(file)['counter_data']

# Load the bridge data for comparison
with open(os.path.join(data_path, 'bridge_tasks_cleaned.json')) as file:
    bridge_tasks_data = json.load(file)['counter_data']
with open(os.path.join(data_path, 'grouped_bridge_objects.json')) as file:
    bridge_objects_data = json.load(file)['counter_data']
with open(os.path.join(data_path, 'normalized_bridge_spatial_relations.json')) as file:
    bridge_spatial_data = json.load(file)['counter_data']

# Convert data to pandas DataFrames
tasks_df = pd.DataFrame(tasks_data.items(), columns=['Task', 'Count']).sort_values(by='Count', ascending=False)
objects_df = pd.DataFrame(objects_data.items(), columns=['Object', 'Count']).sort_values(by='Count', ascending=False)
spatial_df = pd.DataFrame(spatial_data.items(), columns=['Spatial Relation', 'Count']).sort_values(by='Count', ascending=False)
spatial_df = spatial_df[spatial_df['Spatial Relation'] != 'None']

bridge_tasks_df = pd.DataFrame(bridge_tasks_data.items(), columns=['Task', 'Count']).sort_values(by='Count', ascending=False)
bridge_objects_df = pd.DataFrame(bridge_objects_data.items(), columns=['Object', 'Count']).sort_values(by='Count', ascending=False)
bridge_spatial_df = pd.DataFrame(bridge_spatial_data.items(), columns=['Spatial Relation', 'Count']).sort_values(by='Count', ascending=False)
bridge_spatial_df = bridge_spatial_df[bridge_spatial_df['Spatial Relation'] != 'None']

# Calculate maximum y-value for each category
max_tasks_count = max(tasks_df['Count'].max(), bridge_tasks_df['Count'].max())
max_objects_count = max(objects_df['Count'].max(), bridge_objects_df['Count'].max())
max_spatial_count = max(spatial_df['Count'].max(), bridge_spatial_df['Count'].max())

# Plotting function
def plot_distribution(dataframe, title, xlabel, ylabel, color, ymax):
    plt.figure(figsize=(24, 8))
    plt.bar(dataframe.iloc[:, 0], dataframe.iloc[:, 1], color=color)
    plt.yscale('log')
    plt.ylim(1, ymax)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=60, ha='right')
    plt.tight_layout()  # Adjust layout to fit everything
    plt.savefig(f'/home/marcelr/rlds_dataset_builder/data/{title}.png')

# Plot the distribution of tasks, objects, and spatial arrangements with same y-axis range
# plot_distribution(tasks_df.head(100), 'Distribution of LUPUS Tasks', 'Tasks', 'Number of Episodes', 'blue', max_tasks_count)
# plot_distribution(objects_df.head(100), 'Distribution of LUPUS Objects', 'Objects', 'Number of Episodes', 'green', max_objects_count)
# plot_distribution(spatial_df.head(200), 'Distribution of LUPUS Spatial Arrangements', 'Spatial Arrangements', 'Number of Episodes', 'red', max_spatial_count)

# plot_distribution(bridge_tasks_df.head(100), 'Distribution of Default Tasks', 'Tasks', 'Number of Episodes', 'blue', max_tasks_count)# 
# plot_distribution(bridge_objects_df.head(100), 'Distribution of Default Objects', 'Objects', 'Number of Episodes', 'green', max_objects_count)
# plot_distribution(bridge_spatial_df.head(200), 'Distribution of Default Spatial Arrangements', 'Spatial Arrangements', 'Number of Episodes', 'red', max_spatial_count)

def add_objects(lupus_df, bridge_df, fig):

    combined_df = lupus_df.merge(bridge_df, on='Object', how='outer', suffixes=('_lupus', '_bridge'))
    combined_df.fillna(0, inplace=True)
    combined_df['Total Count'] = combined_df['Count_lupus'] + combined_df['Count_bridge']
    combined_df['Max Count'] = np.maximum(combined_df['Count_lupus'], combined_df['Count_bridge'])
    combined_df.sort_values(by='Max Count', ascending=False, inplace=True)
    fontsize = 21
    
    # Calculate ymax dynamically
    ymax = combined_df[['Count_lupus', 'Count_bridge']].max().max() * 1.1  # Add some padding
    # Calculate normalized counts for color mapping
    lupus_counts_norm = combined_df['Count_lupus'] / combined_df['Count_lupus'].max()
    bridge_counts_norm = combined_df['Count_bridge'] / combined_df['Count_bridge'].max()
    # Color gradient for lupus (blue), bride (red) based on normalized counts
    lupus_colors = plt.cm.Blues(0.5 + 0.5 * lupus_counts_norm)
    bridge_colors = plt.cm.Reds(0.5 + 0.5 * bridge_counts_norm)

    ax2 = fig.add_axes([0.389, 0.51, 0.3, 0.45])

    ax2.bar(np.arange(len(combined_df)), combined_df['Count_lupus'], color=lupus_colors, label='NILS Object')
    ax2.bar(np.arange(len(combined_df)), combined_df['Count_bridge'], color=bridge_colors, alpha=0.7, label='Bridge Object')
    
    ax2.set_ylim(0, 8000)
    
    # ax.spines['bottom'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    ax2.set_title("Objects", fontsize=fontsize)
    # ax.tick_params(labelbottom=False)
    ax2.tick_params(labelbottom=False)
    ax2.tick_params(bottom=False)
    # ax.tick_params(bottom=False)
    # ax.set_yscale('linear')
    ax2.set_yscale('linear')
    ax2.set_yticks([0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000])
    ax2.tick_params(axis='y', labelsize=fontsize - 6)

    ax2.set_xticks(np.arange(len(combined_df)))
    # ax2.set_xticklabels(combined_df['Spatial Relation'], rotation=60, ha='right' ,fontsize=fontsize)
    ax2.set_xlim(-0.5, len(combined_df) - 0.5)  # Adjust xlim to reduce space


# plot_combined_spatial_distribution(lupus_df, bridge_df, title, xlabel, ylabel):
def add_spatial(lupus_df, bridge_df, fig):
    combined_df = lupus_df.merge(bridge_df, on='Spatial Relation', how='outer', suffixes=('_lupus', '_bridge'))
    combined_df.fillna(0, inplace=True)
    combined_df['Total Count'] = combined_df['Count_lupus'] + combined_df['Count_bridge']
    combined_df['Max Count'] = np.maximum(combined_df['Count_lupus'], combined_df['Count_bridge'])
    combined_df.sort_values(by='Max Count', ascending=False, inplace=True)
    fontsize = 21
    
    # Calculate ymax dynamically
    ymax = combined_df[['Count_lupus', 'Count_bridge']].max().max() * 1.1  # Add some padding
    # Calculate normalized counts for color mapping
    bridge_counts_norm = combined_df['Count_bridge'] / combined_df['Count_bridge'].max()
    lupus_counts_norm = combined_df['Count_lupus'] / combined_df['Count_lupus'].max()
    # Color gradient for lupus (blue), bride (red) based on normalized counts
    lupus_colors = plt.cm.Blues(0.5 + 0.9 * lupus_counts_norm * 0.5)
    bridge_colors = plt.cm.Reds(0.5 + 0.9 * bridge_counts_norm * 0.5)

    ax2 = fig.add_axes([0.699, 0.51, 0.3, 0.45])
    # ax = ax2.twinx()
    # fig, (ax, ax2) = plt.subplots(2, 1, sharex=True, figsize=(24, 12), gridspec_kw={'height_ratios': [1, 2]})
    bars1 = ax2.bar(np.arange(len(combined_df)), combined_df['Count_lupus'], color=lupus_colors, label='NILS Spatial Relation')
    bars2 = ax2.bar(np.arange(len(combined_df)), combined_df['Count_bridge'], color=bridge_colors, alpha=0.9, label='Bridge Spatial Relation')
    
    
    ax2.set_ylim(0, ymax)

    # ax.spines['bottom'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    # ax.bar(np.arange(len(combined_df)), combined_df['Count_lupus'], color=lupus_colors, label='NILS Spatial Relation')
    # ax.bar(np.arange(len(combined_df)), combined_df['Count_bridge'], color=bridge_colors, alpha=0.9, label='Bridge Spatial Relation')
    # ax.set_ylim(1800, ymax)
    # Add the break lines
    # draw_wavy_break(ax2, position=1200, wavy_width=0.01, wavy_height=25)
    # draw_wavy_break(ax, position=1800, wavy_width=0.01, wavy_height=200)
    
    ax2.set_title("Spatial Relations", fontsize=fontsize)
    # ax.tick_params(labelbottom=False)
    ax2.tick_params(labelbottom=False)
    ax2.tick_params(bottom=False)
    # ax.tick_params(bottom=False)
    # ax.set_yscale('linear')
    ax2.set_yscale('linear')
    ax2.tick_params(axis='y', labelsize=fontsize - 6)

    ax2.set_xticks(np.arange(len(combined_df)))
    # ax2.set_xticklabels(combined_df['Spatial Relation'], rotation=60, ha='right' ,fontsize=fontsize)
    ax2.set_xlim(-0.5, len(combined_df) - 0.5)  # Adjust xlim to reduce space
    ax2.legend(['NILS', "Bridge"], fontsize=fontsize + 4)

# Create the combined plot for spatial relations with an inset for bridge data
def plot_combined_tasks_with_spatial(lupus_df, bridge_df, title, xlabel, ylabel, lupus_color, bridge_color, ymax, xtick_fontsize=20, label_fontsize=22):
    combined_df = lupus_df.merge(bridge_df, on='Task', how='outer', suffixes=('_lupus', '_bridge'))
    combined_df.fillna(0, inplace=True)
    combined_df['Total Count'] = combined_df['Count_lupus'] + combined_df['Count_bridge']
    combined_df['Max Count'] = np.maximum(combined_df['Count_lupus'], combined_df['Count_bridge'])
    # combined_df.sort_values(by='Total Count', ascending=False, inplace=True)
    combined_df.sort_values(by='Max Count', ascending=False, inplace=True)
    offset = 0.5

    # Calculate normalized counts for color mapping if needed
    lupus_counts_norm = combined_df['Count_lupus'] / combined_df['Count_lupus'].max()
    bridge_counts_norm = combined_df['Count_bridge'] / combined_df['Count_bridge'].max()
    
    # Color gradient for lupus based on normalized counts
    lupus_colors = plt.cm.Blues(0.5 + 0.5 * lupus_counts_norm)
    bridge_colors = plt.cm.Reds(0.5 + 0.5 * bridge_counts_norm)


    fig, (ax, ax2) = plt.subplots(2, 1, sharex=True, figsize=(24, 8), gridspec_kw={'height_ratios': [1, 4]})
    # Color gradient for bridge based on normalized counts
    ax2.bar(np.arange(len(combined_df))+offset, combined_df['Count_lupus'], color=lupus_colors, label='NILS Tasks')
    ax2.bar(np.arange(len(combined_df))+offset, combined_df['Count_bridge'], color=bridge_colors, alpha=0.7, label='Bridge Tasks')
    
    ax2.set_ylim(0, 1000)

    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    # Color gradient for bridge based on normalized counts
    # bars1 = ax.bar(lupus_df['Task'], lupus_df['Count'], color=lupus_colors, label='NILS Tasks')
    # bars2 = ax.bar(bridge_df['Task'], bridge_df['Count'], color=bridge_colors, alpha=0.7, label='Bridge Tasks')
    ax.bar(np.arange(len(combined_df))+offset, combined_df['Count_lupus'], color=lupus_colors, label='NILS Tasks')
    ax.bar(np.arange(len(combined_df))+offset, combined_df['Count_bridge'], color=bridge_colors, alpha=0.7, label='Bridge Tasks')
    ax.set_ylim(1500, 40001)
    # Add the break lines
    draw_wavy_break(ax, position=1500, wavy_width=0.01, wavy_height=4000)
    draw_wavy_break(ax2, position=1000, wavy_width=0.01, wavy_height=30)
    
    ax.tick_params(labelbottom=False)
    ax.tick_params(bottom=False)
    ax.set_yscale('linear')
    ax2.set_yscale('linear')
    ax.set_yticks([1500, 10000, 20000, 30000, 40000])
    ax.tick_params(axis='y', labelsize=label_fontsize - 6)
    ax2.set_yticks([0, 200, 400, 600, 800, 1000])
    ax2.tick_params(axis='y', labelsize=label_fontsize - 6)
    # ax.set_ylim(1, ymax)
    ax2.set_xlim(-0.5, len(combined_df) - 0.5)
    ax2.set_xlabel(xlabel, fontsize=label_fontsize)
    ax2.set_ylabel("#of Episodes", fontsize=label_fontsize+2)
    # ax.set_title(title, fontsize=label_fontsize)
    ax2.set_xticks(np.arange(len(combined_df))+offset)
    ax2.set_xticklabels(combined_df['Task'], rotation=60, ha='right', fontsize=xtick_fontsize)

    # Inset plot for bridge data
    add_objects(objects_df.head(60), bridge_objects_df.head(60), fig)
    add_spatial(spatial_df.head(60), bridge_spatial_df.head(60), fig)
    # inset_ax = fig.add_axes([0.65, 0.55, 0.3, 0.4])
    # inset_ax.bar(bridge_df.iloc[:, 0], bridge_df.iloc[:, 1], color=color)
    # # inset_ax.set_yscale('log')
    # inset_ax.set_ylim(1, ymax)
    # inset_ax.set_xticklabels(bridge_df.iloc[:, 0], rotation=60, ha='right')
    # inset_ax.set_title('Bridge Spatial Relations', fontsize=10)

    plt.tight_layout()
    plt.savefig(f'/home/marcelr/rlds_dataset_builder/data/{title}_with_inset.pdf')
    plt.show()

# Plot the combined spatial distribution with an inset for bridge data
plot_combined_tasks_with_spatial(tasks_df.head(60), bridge_tasks_df.head(60), 
                                   'Comparison of Tasks from NILS and default Bridge Labels with', 
                                   'Tasks', 'Number of Episodes', 'blue', 'red', max_tasks_count)


# Create the combined plot for spatial relations with an inset for bridge data
def plot_combined_spatial_distribution(lupus_df, bridge_df, title, xlabel, ylabel, color, ymax):
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.bar(lupus_df.iloc[:, 0], lupus_df.iloc[:, 1], color=color)
    ax.set_yscale('log')
    ax.set_ylim(1, ymax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticklabels(lupus_df.iloc[:, 0], rotation=60, ha='right')

    # Inset plot for bridge data
    inset_ax = fig.add_axes([0.65, 0.55, 0.3, 0.4])
    inset_ax.bar(bridge_df.iloc[:, 0], bridge_df.iloc[:, 1], color=color)
    # inset_ax.set_yscale('log')
    inset_ax.set_ylim(1, ymax)
    inset_ax.set_xticklabels(bridge_df.iloc[:, 0], rotation=60, ha='right')
    inset_ax.set_title('Bridge Spatial Relations', fontsize=10)

    plt.tight_layout()
    plt.savefig(f'/home/marcelr/rlds_dataset_builder/data/{title}_with_inset.pdf')
    plt.show()

# Plot the combined spatial distribution with an inset for bridge data
plot_combined_spatial_distribution(spatial_df.head(60), bridge_spatial_df.head(60), 
                                   'Distribution of NILS Spatial Arrangements with Bridge Inset', 
                                   'Spatial Arrangements', 'Number of Episodes', 'red', max_spatial_count)


def plot_combined_tasks_distribution(lupus_df, bridge_df, title, xlabel, ylabel, lupus_color, bridge_color, ymax, xtick_fontsize=20, label_fontsize=22):
    combined_df = lupus_df.merge(bridge_df, on='Task', how='outer', suffixes=('_lupus', '_bridge'))
    combined_df.fillna(0, inplace=True)
    combined_df['Total Count'] = combined_df['Count_lupus'] + combined_df['Count_bridge']
    combined_df['Max Count'] = np.maximum(combined_df['Count_lupus'], combined_df['Count_bridge'])
    # combined_df.sort_values(by='Total Count', ascending=False, inplace=True)
    combined_df.sort_values(by='Max Count', ascending=False, inplace=True)
    offset = 0.5

    # Calculate normalized counts for color mapping if needed
    lupus_counts_norm = combined_df['Count_lupus'] / combined_df['Count_lupus'].max()
    bridge_counts_norm = combined_df['Count_bridge'] / combined_df['Count_bridge'].max()
    
    # Color gradient for lupus based on normalized counts
    lupus_colors = plt.cm.Blues(0.5 + 0.5 * lupus_counts_norm)
    bridge_colors = plt.cm.Reds(0.5 + 0.5 * bridge_counts_norm)


    fig, (ax, ax2) = plt.subplots(2, 1, sharex=True, figsize=(24, 8), gridspec_kw={'height_ratios': [1, 4]})
    # Color gradient for bridge based on normalized counts
    bars1 = ax2.bar(np.arange(len(combined_df))+offset, combined_df['Count_lupus'], color=lupus_colors, label='NILS Tasks')
    bars2 = ax2.bar(np.arange(len(combined_df))+offset, combined_df['Count_bridge'], color=bridge_colors, alpha=0.7, label='Bridge Tasks')
    
    ax2.set_ylim(0, 1000)

    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    # Color gradient for bridge based on normalized counts
    # bars1 = ax.bar(lupus_df['Task'], lupus_df['Count'], color=lupus_colors, label='NILS Tasks')
    # bars2 = ax.bar(bridge_df['Task'], bridge_df['Count'], color=bridge_colors, alpha=0.7, label='Bridge Tasks')
    ax.bar(np.arange(len(combined_df))+offset, combined_df['Count_lupus'], color=lupus_colors, label='NILS Tasks')
    ax.bar(np.arange(len(combined_df))+offset, combined_df['Count_bridge'], color=bridge_colors, alpha=0.7, label='Bridge Tasks')
    ax.set_ylim(1500, ymax)
    # Add the break lines
    draw_wavy_break(ax, position=1500, wavy_width=0.01, wavy_height=4000)
    draw_wavy_break(ax2, position=1000, wavy_width=0.01, wavy_height=30)
    
    ax.tick_params(labelbottom=False)
    ax.tick_params(bottom=False)
    ax.set_yscale('linear')
    ax2.set_yscale('linear')
    ax.set_yticks([1500, 10000, 20000, 30000])
    ax.tick_params(axis='y', labelsize=label_fontsize - 6)
    # ax2.set_yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500])
    ax2.tick_params(axis='y', labelsize=label_fontsize - 6)
    # ax.set_ylim(1, ymax)
    ax2.set_xlim(-0.5, len(combined_df) - 0.5)
    ax2.set_xlabel(xlabel, fontsize=label_fontsize)
    ax2.set_ylabel("#of Episodes", fontsize=label_fontsize+2)
    ax.set_title(title, fontsize=label_fontsize)
    
    # Find tasks that are only in bridge_df
    # bridge_only_tasks = bridge_df[~bridge_df['Task'].isin(lupus_df['Task'])]
    
    # Set x-ticks and labels
    # all_tasks = lupus_df['Task'].tolist() + bridge_only_tasks['Task'].tolist()
    # ax.set_xticks(np.arange(len(all_tasks)))
    # ax.set_xticklabels(all_tasks, rotation=60, ha='right', fontsize=xtick_fontsize)
    ax2.set_xticks(np.arange(len(combined_df))+offset)
    ax2.set_xticklabels(combined_df['Task'], rotation=60, ha='right', fontsize=xtick_fontsize)
    
    ax.legend(fontsize=label_fontsize+6)
    plt.tight_layout()
    plt.savefig(f'/home/marcelr/rlds_dataset_builder/data/{title}.pdf')

# Plot the combined tasks distribution with overlaid bridge data
plot_combined_tasks_distribution(tasks_df.head(60), bridge_tasks_df.head(60), 
                                 'Comparison of Tasks from NILS and default Bridge Labels', 
                                 'Tasks', 'Number of Episodes', 
                                 'blue', 'red', max_tasks_count)


def plot_combined_object_distribution(lupus_df, bridge_df, title, xlabel, ylabel, lupus_color, bridge_color, ymax, xtick_fontsize=20, label_fontsize=21):
    # Combine the dataframes to ensure we include all objects
    combined_df = lupus_df.merge(bridge_df, on='Object', how='outer', suffixes=('_lupus', '_bridge'))
    combined_df.fillna(0, inplace=True)
    combined_df['Total Count'] = combined_df['Count_lupus'] + combined_df['Count_bridge']
    combined_df['Max Count'] = np.maximum(combined_df['Count_lupus'], combined_df['Count_bridge'])
    # combined_df.sort_values(by='Total Count', ascending=False, inplace=True)
    combined_df.sort_values(by='Max Count', ascending=False, inplace=True)
    offset = 0.5

    # Calculate normalized counts for color mapping if needed
    lupus_counts_norm = combined_df['Count_lupus'] / combined_df['Count_lupus'].max()
    bridge_counts_norm = combined_df['Count_bridge'] / combined_df['Count_bridge'].max()
    
    # Color gradient for lupus based on normalized counts
    lupus_colors = plt.cm.Blues(0.5 + 0.5 * lupus_counts_norm)
    bridge_colors = plt.cm.Reds(0.5 + 0.5 * bridge_counts_norm)
    
    fig, (ax, ax2) = plt.subplots(2, 1, sharex=True, figsize=(24, 10), gridspec_kw={'height_ratios': [1, 8]})
    ax2.bar(np.arange(len(combined_df))+offset, combined_df['Count_lupus'], color=lupus_colors, label='NILS Object')
    ax2.bar(np.arange(len(combined_df))+offset, combined_df['Count_bridge'], color=bridge_colors, alpha=0.7, label='Bridge Object')

    ax2.set_ylim(0, 3700)

    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    ax.bar(np.arange(len(combined_df))+offset, combined_df['Count_lupus'], color=lupus_colors, label='NILS Object')
    ax.bar(np.arange(len(combined_df))+offset, combined_df['Count_bridge'], color=bridge_colors, alpha=0.7, label='Bridge Object')
    ax.set_ylim(4500, ymax)
    # Add the break lines
    draw_wavy_break(ax, position=4500, wavy_width=0.01, wavy_height=350)
    draw_wavy_break(ax2, position=3700, wavy_width=0.01, wavy_height=50)
    
    ax.tick_params(labelbottom=False)
    ax.tick_params(bottom=False)
    ax.set_yscale('linear')
    ax2.set_yscale('linear')
    # ax.set_yticks([7500, 8000])
    # ax2.set_yticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500])
    ax.tick_params(axis='y', labelsize=label_fontsize - 5)
    ax2.tick_params(axis='y', labelsize=label_fontsize - 5)
    # ax.set_ylim(1, ymax)
    ax2.set_xticks(np.arange(len(combined_df))+offset)
    ax2.set_xticklabels(combined_df['Object'], rotation=60, ha='right', fontsize=xtick_fontsize)
    ax2.set_xlim(-0.5, len(combined_df) - 0.5)
    ax2.set_xlabel(xlabel, fontsize=label_fontsize)
    ax2.set_ylabel("#of Episodes", fontsize=label_fontsize+5)
    ax.set_title(title, fontsize=label_fontsize)
    ax.legend(fontsize=label_fontsize+6)
    
    # plt.setp(ax.get_xticklabels(), visible=False)
    plt.tight_layout()
    plt.savefig(f'/home/marcelr/rlds_dataset_builder/data/{title}.pdf')


# Plot the combined tasks distribution with overlaid bridge data
plot_combined_object_distribution(objects_df.head(60), bridge_objects_df.head(60), 
                                 'Comparison of Objects from NILS and default Bridge Labels', 
                                 'Objects', 'Number of Episodes', 
                                 'blue', 'red', max_objects_count)


def plot_combined_spatial_distribution(lupus_df, bridge_df, title, xlabel, ylabel):
    combined_df = lupus_df.merge(bridge_df, on='Spatial Relation', how='outer', suffixes=('_lupus', '_bridge'))
    combined_df.fillna(0, inplace=True)
    combined_df['Total Count'] = combined_df['Count_lupus'] + combined_df['Count_bridge']
    combined_df['Max Count'] = np.maximum(combined_df['Count_lupus'], combined_df['Count_bridge'])
    combined_df.sort_values(by='Max Count', ascending=False, inplace=True)
    fontsize = 21
    offset = 0.5
    
    # Calculate ymax dynamically
    ymax = combined_df[['Count_lupus', 'Count_bridge']].max().max() * 1.1  # Add some padding
    # Calculate normalized counts for color mapping
    bridge_counts_norm = combined_df['Count_bridge'] / combined_df['Count_bridge'].max()
    lupus_counts_norm = combined_df['Count_lupus'] / combined_df['Count_lupus'].max()
    # Color gradient for lupus (blue), bride (red) based on normalized counts
    lupus_colors = plt.cm.Blues(0.5 + 0.9 * lupus_counts_norm * 0.5)
    bridge_colors = plt.cm.Reds(0.5 + 0.9 * bridge_counts_norm * 0.5)
    
    fig, (ax, ax2) = plt.subplots(2, 1, sharex=True, figsize=(24, 12), gridspec_kw={'height_ratios': [1, 2]})
    ax2.bar(np.arange(len(combined_df))+offset, combined_df['Count_lupus'], color=lupus_colors, label='NILS Spatial Relation')
    ax2.bar(np.arange(len(combined_df))+offset, combined_df['Count_bridge'], color=bridge_colors, alpha=0.9, label='Bridge Spatial Relation')
    
    
    ax2.set_ylim(0, 1200)

    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    ax.bar(np.arange(len(combined_df))+offset, combined_df['Count_lupus'], color=lupus_colors, label='NILS Spatial Relation')
    ax.bar(np.arange(len(combined_df))+offset, combined_df['Count_bridge'], color=bridge_colors, alpha=0.9, label='Bridge Spatial Relation')
    ax.set_ylim(1800, ymax)
    # Add the break lines
    draw_wavy_break(ax2, position=1200, wavy_width=0.01, wavy_height=25)
    draw_wavy_break(ax, position=1800, wavy_width=0.01, wavy_height=200)
    
    ax.tick_params(labelbottom=False)
    ax.tick_params(bottom=False)
    ax.set_yscale('linear')
    ax2.set_yscale('linear')
    ax.set_yticks([2000, 3000, 4000, 5000, 6000, 7000])
    ax2.set_yticks([0, 250, 500, 750, 1000])
    ax.tick_params(axis='y', labelsize=fontsize - 5)
    ax2.tick_params(axis='y', labelsize=fontsize - 5)
    
    # ax.set_yscale('asinh')
    # ax.set_ylim(1, ymax)
    ax2.set_xticks(np.arange(len(combined_df))+offset)
    ax2.set_xticklabels(combined_df['Spatial Relation'], rotation=60, ha='right' ,fontsize=fontsize)
    ax2.set_xlim(-0.5, len(combined_df) - 0.5)  # Adjust xlim to reduce space
    ax2.set_xlabel(xlabel,fontsize=fontsize)
    ax2.set_ylabel("#of Episodes",fontsize=fontsize+5)
    ax.set_title(title,fontsize=fontsize)
    ax.legend(fontsize=fontsize+6)
    
    plt.tight_layout()
    plt.savefig(f'/home/marcelr/rlds_dataset_builder/data/{title}.pdf')




# Plot the combined tasks distribution with overlaid bridge data
plot_combined_spatial_distribution(spatial_df.head(60), bridge_spatial_df.head(60), 
                                 'Comparison of Spatial Relations from NILS and default Bridge Labels', 
                                 'Spatial Relation', 'Number of Episodes')
                                #  'blue', 'red',) # max_spatial_count)

print('Done')