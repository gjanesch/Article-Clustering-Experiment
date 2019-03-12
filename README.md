# Article Clustering Experiment

This is an experiment to see how effective news article clustering can be.  It uses articles from the IEEE Spectrum website, as all articles there are clearly categorized, meaning the algorithm's output can be compared to the real classes.

<tt>article_df.csv</tt> is a tab-delimited file containing the article texts used in this experiment, while <tt>13 clusters.csv</tt> and <tt>26 clusters.csv</tt> are cross-tabulations of clustering results with the articles' original categories.

Packages used: <tt>newspaper</tt>, <tt>pandas</tt>, <tt>numpy</tt>, <tt>bs4</tt> (BeautifulSoup), <tt>tqdm</tt>