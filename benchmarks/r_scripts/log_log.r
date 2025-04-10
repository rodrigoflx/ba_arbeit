library(tidyverse)
library(optparse)
library(glue)

option_list <- list(
  make_option(
    c("--output", "-o"),
    type = "character",
    help = "Output file path",
    metavar = "string"
  )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser, positional_arguments = TRUE)

file_path <- opt$args
output <- opt$options$output

file_path <- as.character(file_path)

data <- read_csv(file_path)

ggplot(data,
    aes(x = entry,
        y = cnt)) +
    geom_point() +
    scale_y_log10() +
    scale_x_log10() +
    ylab("Log counts") +
    xlab("Log buckets") +
    theme_bw() +

ggsave(output, width = 6, height = 4)