import git
import sys

branch = "Test_Branch"
origin = "https://github.com/Khoa-Nguyen-Kevin/CodeRace_Round-3_Data-Migration.git"
input_file_path = sys.argv[1]
#Initialize repository
repo = git.Repo.init()

#Add rst file
repo.index.add(input_file_path)
#Commit
repo.index.commit("Commit rst")
#Move to branch, if branch does not exist, create it.
repo.git.checkout("-B", branch)
#Push to origin repository at branch
repo.git.push(origin, branch)

print("Push Success")