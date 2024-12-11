import re
import pandas as pd

# helper function to extract names 
def extract_names_from_list(list_with_names: list[str]) -> list[str]:
    # Define a regex pattern to match lines that contain a " * " followed by a name
    name_pattern = r'\* ([A-Za-z\s\.\,]+)'

    # Extract names using regex
    names = [re.findall(name_pattern, entry) for entry in list_with_names]
    names = [name[0] for name in names if name]  # Flatten the result and remove empty entries

    return names

# common terms to define distinct parts in Earning Call transcripts by Refinitiv 
search_terms = ["Corporate Participants", "Conference Call Participiants", "Presentation", "Questions and Answers"]


def convert_transcript_to_df(transcript):
    # split by lines with - and = symbols
    split_by_lines_and_equal_signs = re.split(r'[-=]{5,}', transcript)

    # find where different parts begin
    found_indices = {}
    for idx, entry in enumerate(split_by_lines_and_equal_signs):
        for term in search_terms:
            if term in entry:
                if term in found_indices:
                    print("One of the search terms appeared more than once")
                found_indices[term] = idx

    # extract participant names
    corporate_members = extract_names_from_list(split_by_lines_and_equal_signs[found_indices["Corporate Participants"] + 1].split("\n"))
    non_corporate_members = extract_names_from_list(split_by_lines_and_equal_signs[found_indices["Conference Call Participiants"] + 1].split("\n"))
    participants = corporate_members + non_corporate_members

    # get presentation part
    presentation_part = split_by_lines_and_equal_signs[found_indices["Presentation"] + 1:found_indices["Questions and Answers"]]
    # get Q&A part
    q_and_a_part = split_by_lines_and_equal_signs[found_indices["Questions and Answers"]+1:]

    earning_call = pd.DataFrame(columns = ["name", "text", "action"])
    earning_call_idx = 0
    for idx, line in enumerate(presentation_part):
        for name in participants:
            if line.startswith(f"\n{name}"):
                earning_call.loc[earning_call_idx, :] = [name, presentation_part[idx + 1].replace("\n", " ").strip(), "presentation"]
                earning_call_idx += 1

    for idx, line in enumerate(q_and_a_part):
        for name in participants:
            if line.startswith(f"\n{name}"):
                earning_call.loc[earning_call_idx, :] = [name, q_and_a_part[idx + 1].replace("\n", " ").strip(), "q_and_a"]
                earning_call_idx += 1

    earning_call.loc[:, "responsibility"] = ["firm" if name in corporate_members else "analyst" for name in earning_call.name]
    
    return earning_call

