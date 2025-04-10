library(ggplot2)
library(Cairo)
library(RColorBrewer)
library(glue)
library(optparse)
library(scales)
library(dplyr)

find_generator_in_path <- function(path) {
  # Assumes the generator is the last directory in the path
  return (basename(dirname(path)))
}

plot_distributions <- function(file_paths, skew, samples, n, buckets, new_buckets, output_path) {
  generator <- find_generator_in_path(file_paths) 
  data <- read.csv(file_paths)

  # ensure required columns exist
  required_cols <- c("entry", "cnt", "rel_freq")
  if (!all(required_cols %in% colnames(data))) {
    stop("the input csv file must contain the columns: entry, cnt, rel_freq.")
  }

  data$generator <- generator

  # Recalculate rel_freq by rebucketing the data
  data <- data %>%
    mutate(new_entry = floor(entry / (buckets / new_buckets))) %>%
    group_by(new_entry) %>%
    summarise(cnt = sum(cnt), rel_freq = sum(rel_freq), .groups = 'drop') %>%
    rename(entry = new_entry)

  # Adjust the x-axis to match the new bucket range
  buckets <- new_buckets

  zipfdist <- ggplot(data,
                     aes(x = .data$entry,
                         y = .data$rel_freq * 100)) +
    geom_line() +
    scale_y_log10(breaks = c(0.001, 0.01, 0.1, 0.5, 1, 2, 5, 10, 20, 40)) +
    ylab("Accesses [%]") +
    xlab("Histogram Buckets") +
    theme_bw() 

    ggsave(output_path, plot = zipfdist, width = 4, height = 2)

    # CairoPDF(output_path, width = 8, height = 6, bg = "transparent")
    # print(zipfdist)
    # dev.off() 
}
option_list <- list(
  make_option(
    c("--n"),
    type = "integer",
    help = "Number of elements",
    metavar = "int"
  ),
  make_option(
    c("--samples"),
    type = "integer",
    help = "Number of samples",
    metavar = "int"),
  make_option(
    c("--skew"),
    type = "double",
    help = "Skew factor",
    metavar = "float"
  ),
  make_option(
    c("--output"),
    type = "character",
    help = "Output file path",
    metavar = "file"
  ),
  make_option(
    c("--buckets"),
    type = "integer",
    help = "Number of buckets",
    metavar = "int"
  ),
  make_option(
    c("--new_buckets"),
    type = "integer",
    help = "Number of new buckets",
    metavar = "int"
  )
)

# Parse command-line arguments
opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser, positional_arguments = TRUE)

# Extract the arguments
n <- opt$options$n
samples <- opt$options$samples
skew <- opt$options$skew
output_path <- opt$options$output
buckets <- opt$options$buckets
new_buckets <- opt$options$new_buckets

file_paths <- opt$args

file_paths <- as.character(file_paths)

# Call the function with the provided arguments
plot_distributions(file_paths, skew, samples, n, buckets, new_buckets, output_path)