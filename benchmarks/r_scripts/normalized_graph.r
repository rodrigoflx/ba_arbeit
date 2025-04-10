library(tidyverse)
library(optparse)
library(glue)

bucketized_dzipf <- function(n, exponent, buckets) {
  zipf_denominator <- sum(1 / (1:n)^exponent)

  bucket_size <- ceiling(n / buckets)
  bucket_edges <- seq(1, n + 1, by = bucket_size)
  
  bucket_pmf <- numeric(length(bucket_edges) - 1)

  for (i in seq_along(bucket_pmf)) {
    bucket_start <- bucket_edges[i]
    bucket_end <- min(bucket_edges[i + 1] - 1, n)
    bucket_pmf[i] <- sum(1 / (bucket_start:bucket_end)^exponent) / zipf_denominator
  }

  bucket_df = data.frame(
    entry = 0:(buckets - 1),
    theo_freq = bucket_pmf
  )

  return(bucket_df)
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
    c("--output", "-o"),
    type = "character",
    help = "Output file path",
    metavar = "string"
  ),
  make_option(
    c("--buckets", "-b"),
    type = "integer",
    help = "Number of buckets",
    metavar = "int"
  )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser, positional_arguments = TRUE)

n <- opt$options$n
samples <- opt$options$samples
exponent <- opt$options$skew
file_path <- opt$args
output <- opt$options$output
buckets <- opt$options$buckets

file_path <- as.character(file_path)

data <- read_csv(file_path)

# Add the theoretical frequency to the data
bucket_theoretical_df <- bucketized_dzipf(n, exponent, buckets)

data <- data %>%
  inner_join(bucket_theoretical_df, by = "entry")

data <- data %>%
  mutate(ratio = rel_freq / theo_freq)

ggplot(data, aes(x = entry, y = ratio)) +
  geom_hline(yintercept = 1, color = '#0066ff83') +
  geom_point(color = '#c78442') +
  labs(x = "Rank", y = expression(f[emp]/f[theo])) +
  ylim(c(0,2)) +
  xlim(c(0, buckets - 1)) +
  theme_bw()

ggsave(output, width = 6, height = 4)