import os
import logging
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class RecommendationTrends() :
    def __init__(self, sb : list, b: list, h: list, s: list, ss: list, dates: list):

        # Reverse the data set so the graphs show up in increasing months order on the x-axis
        self.sb = sb[::-1]
        self.b = b[::-1]
        self.h = h[::-1]
        self.s = s[::-1]
        self.ss = ss[::-1]

        # Map numeric date to month
        date_list = [self.convert_to_string_month(date) for date in dates]
        self.dates = date_list[::-1]

    @staticmethod
    def convert_to_string_month(full_date):
        """
        Converts a full date in YYYY-MM-DD format (e.g., '2025-01-01')
        to a string month (e.g., 'January').
        """
        try:
            # Parse the full date
            date_obj = datetime.datetime.strptime(full_date, "%Y-%m-%d")
            return date_obj.strftime("%B")  # Convert to month name
        except ValueError as e:
            raise ValueError(f"Invalid date format: {full_date}. Expected format is 'YYYY-MM-DD'.") from e


def gen_bar_graph_recommended_trends(ticker : str, rt: RecommendationTrends) -> str: 
    """
    This function creates a recommendation trends bar graph for the specific ticker 
    and returns the image path
    """

    data_rating_set = {
        "Strong Sell": rt.ss, 
        "Sell": rt.s, 
        "Hold": rt.h, 
        "Buy": rt.b, 
        "Strong Buy": rt.sb
    } 
    color_map = {
        "Strong Sell": "#ff0000",  # Red
        "Sell": "#FFA500",         # Orange
        "Hold": "#fffc33",         # Yellow
        "Buy": "#7aff33",          # Green
        "Strong Buy": "#228B22"    # Forest Green
    }

    # Create the bar graph using a data frame
    df = pd.DataFrame(data_rating_set, index=rt.dates)
    ax = df.plot.bar(stacked=True, color=color_map, rot=0)

    # Add title and axis labels
    plt.title(f"{ticker} Recommendation Trends")
    plt.xlabel("Months")
    plt.ylabel("Number of Analyists")

    # Add legend at the bottom
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles, 
        labels,
        loc="upper center", 
        bbox_to_anchor=(0.5, -0.15),
        ncol=5, 
        title="Ratings"
    )

    # Adjust layout to prevent cutting off the bottom
    plt.tight_layout()

    # Save the figure
    graph_dir = "matplotlib_graphs"
    os.makedirs(graph_dir, exist_ok=True)
    img_path = os.path.join(os.getcwd(), graph_dir, ticker + "_recommendation_trends_bar.png")
    plt.savefig(img_path)
    plt.close() # Close the plot to avoid memory issues

    return img_path
    

def gen_line_graph_recommended_trends(ticker : str, rt: RecommendationTrends) -> str:
    """
    This function creates a recommendation trends line graph for the specific ticker 
    over time and returns the image path. 

    Additionally, it will only produce 3 lines in total.
    It will combine strong buy and buy into just one buy category. 
    It will do this for the strong sell and sell as well. 
    Holds will remain the same.
    """

    # Combine the buys and sells into one line each
    buy = [x + y for x, y in zip(rt.b, rt.sb)]
    sell = [x + y for x, y in zip(rt.s, rt.ss)]

    data_rating_set = {
        "Sell": sell, 
        "Hold": rt.h, 
        "Buy": buy
    } 
    color_map = {
        "Sell": "#ff0000",  # Red
        "Hold": "#FFA500",  # Orange
        "Buy": "#228B22"    # Forest Green
    }
    
    # Create the bar graph using a data frame
    df = pd.DataFrame(data_rating_set, index=rt.dates)
    ax = df.plot.line(color=color_map, marker='o', rot=0)

    # Add title and axis labels
    plt.title(f"{ticker} Recommendation Trends")
    plt.xlabel("Months")
    plt.ylabel("Number of Analyists")

    # Label each point on the graph
    for line_name, line_data in data_rating_set.items():
        for x, y in enumerate(line_data):
            ax.annotate(
                text=str(y), # Text to display (the value at the point)
                xy=(x, y),   # Position of the point (x, y)
                xytext=(0, 5),  # Adjust offset dynamically
                textcoords="offset points",
                ha="center",     # Horizontal alignment
                fontsize=8,      # Font size for the label
                color=color_map[line_name] # Match label color with the line
            )
           
    # Add legend at the bottom
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles, 
        labels, 
        loc="upper center", 
        bbox_to_anchor=(0.5, -0.15),
        ncol=3, 
        title="Ratings"
    )

    # Adjust layout to prevent cutting off the bottom
    plt.tight_layout()

    # Save the figure
    graph_dir = "matplotlib_graphs"
    os.makedirs(graph_dir, exist_ok=True)
    img_path = os.path.join(os.getcwd(), graph_dir, ticker + "_recommendation_trends_line.png")
    plt.savefig(img_path)
    plt.close() # Close the plot to avoid memory issues

    return img_path
