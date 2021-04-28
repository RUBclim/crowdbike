library(lintr)
library(tools)


lint_my_script <- function(filename, line_length = 80, object_length = 20) {
  if (!file.exists(filename)) {
    stop(paste('File not found "', filename, '"', sep = ''))
  }
  else if (file_ext(filename) != 'r' & file_ext(filename) != 'R')  {
    stop(paste('Not supported file type "', file_ext(filename), '"', sep = ''))
  }
  else {
  lint(
    filename = filename,
    linters = c(pipe_continuation_linter,
                object_usage_linter,
                assignment_linter,
                closed_curly_linter,
                cyclocomp_linter,
                equals_na_linter,
                function_left_parentheses_linter,
                infix_spaces_linter,
                line_length_linter(length = line_length),
                no_tab_linter,
                object_length_linter(length = object_length),
                object_name_linter(styles = c('camelCase', 'snake_case')),
                paren_brace_linter,
                seq_linter,
                spaces_inside_linter,
                todo_comment_linter, # FIXME does not work
                trailing_whitespace_linter,
                undesirable_function_linter,
                undesirable_operator_linter,
                unneeded_concatenation_linter)
        )
    }
}
