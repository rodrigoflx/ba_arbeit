library(optparse)
library(jsonlite)
library(ggplot2)
library(dplyr)
library(latex2exp)

theme_set(theme_bw())

opt_parser <- OptionParser(option_list = c())
opt <- parse_args(opt_parser, positional_arguments = TRUE)

files_paths <- opt$args

files_paths <- as.character(files_paths)

data_list <- list()

# Loop over each JSON file
for(file in files_paths) {
  # Read the JSON file
  json_data <- fromJSON(file)
  
  # Extract the 'n' value from metadata
  n_val <- json_data$metadata$n
  
  # Loop over each sampler in the results and extract the 'tvd'
  for(sampler in names(json_data$results)) {
    tvd_val <- json_data$results[[sampler]]$tvd
    
    # Create a data frame for this sampler and JSON file
    temp_df <- data.frame(
      n = n_val,
      sampler = sampler,
      tvd = tvd_val,
      stringsAsFactors = FALSE
    )
    
    # Append to our list
    data_list[[length(data_list) + 1]] <- temp_df
  }
}

# Combine all the data into one data frame
df <- bind_rows(data_list)

# Plot TVD against n for each sampler
p <- ggplot(df, aes(x = n, y = tvd, color = sampler, group = sampler)) +
  geom_line() +
  geom_point() +
  labs(
    title = "Total Variation Distance vs. Domain Size",
    x = TeX("n"),
    y = TeX("TVD")
  ) +
  theme(
    axis.title.x = element_text(margin = margin(t = 10), size = 12),
    axis.title.y = element_text(margin = margin(t = 10), size = 12),
    plot.title = element_text(face = "bold",
                              size = 14,
                              hjust = 0.5,
                              margin = margin(10, 0, 10, 0)),
  )
# Optionally, save the plot to a file
ggsave("TVD_vs_n.png", plot = p, width = 8, height = 6)