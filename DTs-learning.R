library("C50") # load the package

process_data <- function(rules_path) {
  folder_path <- paste(rules_path, "\\", sep = "")
  csv_files <- list.files(path = folder_path, pattern = "\\.csv$", full.names = TRUE)
  for (file in csv_files) {
    data <- read.csv(file) # read the dataset
    if (is.data.frame(data) && nrow(data) == 0) {
      error_message <- paste("Error: Dataset in file", file, "is empty.")
      return(error_message)
    }
    dim <- ncol(data)
    rules <- C5.0(data.frame(Feature = data[, 1]), as.factor(data[, dim]), rules = TRUE)
    file <- sub(".csv", "", file)
    rules_file <- paste(file, ".txt")
    write(capture.output(summary(rules)), rules_file)
  }
  return(NULL)  # No error occurred
}

#domain_name <- "driverlog"
#process_data(domain_name)
