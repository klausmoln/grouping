import tkinter as tk
from tkinter import messagebox
import json
import os
import random


class Person:
    def __init__(self, name, gender, spouse=None):
        self.name = name
        self.gender = gender
        self.spouse = spouse


def save_people():
    with open("people.json", "w", encoding="utf-8") as f:
        json_people = [
            {"name": person.name, "gender": person.gender, "spouse": person.spouse}
            for person in people
        ]
        json.dump(json_people, f, ensure_ascii=False, indent=4)


def load_people():
    if os.path.exists("people.json"):
        with open("people.json", "r", encoding="utf-8") as f:
            json_people = json.load(f)
            for person_data in json_people:
                person = Person(person_data["name"], person_data["gender"], person_data["spouse"])
                people.append(person)
                listbox_people.insert(tk.END, f"{person.name} ({person.gender})")


def add_person():
    name = entry_name.get()
    gender = var_gender.get()
    spouse = entry_spouse.get()
    if not name or not gender:
        messagebox.showerror("输入错误", "请填写完整的信息")
        return
    person = Person(name, gender, spouse)
    people.append(person)
    listbox_people.insert(tk.END, f"{name} ({gender})")
    entry_name.delete(0, tk.END)
    entry_spouse.delete(0, tk.END)
    save_people()


def delete_person():
    selected_indices = list(listbox_people.curselection())
    if not selected_indices:
        messagebox.showerror("选择错误", "请先选择要删除的人")
        return

    # Ensure to process indices in reverse order to avoid shifting issues
    for index in sorted(selected_indices, reverse=True):
        person_str = listbox_people.get(index)
        name = person_str.split(' ')[0]
        
        # Find the person in the people list by name and remove
        for person in people:
            if person.name == name:
                if messagebox.askyesno("确认删除",f"是否确认删除\"{name}\"？"):
                    people.remove(person)
                    break
                else:
                    return

        # Remove from listbox
        listbox_people.delete(index)

    save_people()


def show_groups():
    if len(people) < 6:
        messagebox.showerror("输入错误", "人数不足，无法分组")
        return
    groups = create_groups(people)
    result = ""
    for i, group in enumerate(groups):
        result += f"Group {i + 1}:\n"
        for person in group:
            result += f"  {person.name} ({person.gender})\n"
    messagebox.showinfo("分组结果", result)


def separate_spouses(groups):
    for group in groups:
        spouses = set()
        for person in group:
            if person.spouse in spouses:
                return False
            if person.spouse:
                spouses.add(person.name)
    return True


def check_gender_balance(groups):
    for group in groups:
        males = sum(1 for person in group if person.gender == 'M')
        females = sum(1 for person in group if person.gender == 'F')
        if males < 2 or females < 2:
            return False
    return True


def create_groups(people):
    while True:
        random.shuffle(people)
        groups = [people[i::3] for i in range(3)]
        if separate_spouses(groups) and check_gender_balance(groups):
            return groups


# 初始化人员列表
people = []

# 创建主窗口
root = tk.Tk()
root.title("随机分组")

# 创建输入框和标签
label_name = tk.Label(root, text="姓名:")
label_name.grid(row=0, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1)

label_gender = tk.Label(root, text="性别:")
label_gender.grid(row=1, column=0)
var_gender = tk.StringVar(value="M")
radio_male = tk.Radiobutton(root, text="男", variable=var_gender, value="M")
radio_male.grid(row=1, column=1)
radio_female = tk.Radiobutton(root, text="女", variable=var_gender, value="F")
radio_female.grid(row=1, column=2)

label_spouse = tk.Label(root, text="配偶:")
label_spouse.grid(row=2, column=0)
entry_spouse = tk.Entry(root)
entry_spouse.grid(row=2, column=1)

# 创建添加按钮
button_add = tk.Button(root, text="添加", command=add_person)
button_add.grid(row=3, column=0)

# 创建删除按钮
button_delete = tk.Button(root, text="删除", command=delete_person)
button_delete.grid(row=3, column=1)

# 创建显示人员列表的列表框
listbox_people = tk.Listbox(root, selectmode=tk.MULTIPLE)  # 允许多选
listbox_people.grid(row=4, column=0, columnspan=3)

# 创建分组按钮
button_group = tk.Button(root, text="随机分组", command=show_groups)
button_group.grid(row=5, column=1)

# 载入人员信息
load_people()

# 运行主循环
root.mainloop()
