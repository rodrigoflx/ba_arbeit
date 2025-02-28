library(tidyverse)
library(optparse)
library(glue)

dzipf <- function(rank, total_counts, exponent = 1) {
  zipf_denominator <- sum(1 / (1:total_counts)^exponent)
  return(1 / ((rank)^exponent * zipf_denominator))
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
  )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser, positional_arguments = TRUE)

n <- opt$options$n
samples <- opt$options$samples
exponent <- opt$options$skew
file_path <- opt$args

file_path <- as.character(file_path)

data <- read_csv(file_path)

# Add the theoretical frequency to the data
data <- data %>%
  mutate(theoretical_frequency = dzipf(entry, nrow(data), exponent))

data <- data %>%
  mutate(ratio = rel_freq / theoretical_frequency)

ggplot(data, aes(x = entry, y = log(ratio))) +
  geom_hline(yintercept = 1, color = '#0066ff83') +
  geom_point(color = '#ff880083') +
  labs(title = "Ratio of Empirical to Theoretical Generalized Zipf Frequencies",
       x = "Rank",
       y = "Empirical/Theoretical Frequency Ratio",
       caption = glue("Exponent {exponent}, Samples {samples}, Domain {n}")) +
  theme_minimal()