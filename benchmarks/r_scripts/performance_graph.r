#!/usr/bin/env Rscript

# Load required libraries
library(jsonlite)
library(ggplot2)
library(patchwork)

# Get command line arguments (JSON file paths)
args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 0) {
  stop("Please provide at least one JSON file path as a positional argument.")
}

data_list <- list()

for (file in args) {
  json_data <- fromJSON(file)
  samples <- json_data$metadata$samples
  
  df <- data.frame(
    sampler = names(json_data$results),
    milliseconds = as.numeric(unlist(json_data$results)),
    stringsAsFactors = FALSE
  )
  
  df$samples <- samples
  
  data_list[[file]] <- df
}

plot_list <- list()

for (file in args) {
  df <- data_list[[file]]
  
  p <- ggplot(df, aes(x = 1, y = milliseconds, color = sampler)) +
    geom_point(size = 3) +
    labs(
      y = "Milliseconds",
      color = "Sampler",
      caption = paste("Samples:", format(df$samples[1], big.mark = ","))
    ) +
    theme_minimal() +
    theme(
      axis.title.x = element_blank(),
      axis.text.x  = element_blank(),
      axis.ticks.x = element_blank()
    )
  plot_list[[file]] <- p
}

combined_plot <- wrap_plots(plot_list, ncol = length(plot_list)) +
  plot_layout(guides = "collect") &
  theme(legend.position = "right")

final_plot <- combined_plot +
  plot_annotation(
    title = "Sampler Performance",
    theme = theme(plot.title = element_text(size = 16, hjust = 0.5))
  )

ggsave(
  filename = "sampler_performance_no_alignment.png",
  plot = final_plot,
  width = 12,
  height = 5,
  dpi = 300
)
