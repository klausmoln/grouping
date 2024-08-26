import tkinter as tk
from tkinter import messagebox
import json
import os
import random
import time


class Person:
    def __init__(self, name, gender, location, spouse=None):
        self.name = name
        self.gender = gender
        self.location = location
        self.spouse = spouse


def save_people():
    with open("people.json", "w", encoding="utf-8") as f:
        json_people = [
            {"name": person.name, "gender": person.gender, "location": person.location, "spouse": person.spouse}
            for person in people + not_participating_list
        ]
        json.dump(json_people, f, ensure_ascii=False, indent=4)


# 保存当前分组结果到文件
def save_last_groups(groups):
    # 将当前分组保存为 JSON 文件
    with open("last_groups.json", "w", encoding="utf-8") as f:
        json_groups = [
            [person.name for person in group] for group in groups
        ]
        json.dump(json_groups, f, ensure_ascii=False, indent=4)


# 读取上一次的分组结果
def load_last_groups():
    if os.path.exists("last_groups.json"):
        with open("last_groups.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def refresh_listboxes():
    listbox_offline.delete(0, tk.END)
    listbox_online.delete(0, tk.END)
    listbox_not_participating.delete(0, tk.END)
    male_list.clear()
    female_list.clear()

    for person in people:
        if person.gender == "M":
            male_list.append(person)
        else:
            female_list.append(person)

        if person.location == "On-site":
            listbox_offline.insert(tk.END, f"{person.name} ({person.gender})")
        else:
            listbox_online.insert(tk.END, f"{person.name} ({person.gender})")

    for person in not_participating_list:
        listbox_not_participating.insert(tk.END, f"{person.name} ({person.gender})")
    label_current_count.config(text=f"当前人数：{len(people)}")


def load_people():
    if os.path.exists("people.json"):
        with open("people.json", "r", encoding="utf-8") as f:
            json_people = json.load(f)
            for person_data in json_people:
                person = Person(person_data["name"], person_data["gender"], person_data["location"],
                                person_data["spouse"])
                if person.location == "Not Participating":
                    not_participating_list.append(person)
                else:
                    people.append(person)
                    if person.gender == "M":
                        male_list.append(person)
                    else:
                        female_list.append(person)

                    if person.location == "On-site":
                        listbox_offline.insert(tk.END, f"{person.name} ({person.gender})")
                    else:
                        listbox_online.insert(tk.END, f"{person.name} ({person.gender})")

            for person in not_participating_list:
                listbox_not_participating.insert(tk.END, f"{person.name} ({person.gender})")


def add_person():
    name = entry_name.get()
    gender = var_gender.get()
    location = var_location.get()
    spouse = entry_spouse.get()
    if not name or not gender or not location:
        messagebox.showerror("输入错误", "请填写完整的信息")
        return
    person = Person(name, gender, location, spouse)
    people.append(person)
    save_people()
    refresh_listboxes()
    entry_name.delete(0, tk.END)
    entry_spouse.delete(0, tk.END)


def delete_person():
    def remove_person(listbox):
        selected_indices = list(listbox.curselection())
        if not selected_indices:
            #    messagebox.showerror("选择错误", "请先选择要删除的人")
            return

        for index in sorted(selected_indices, reverse=True):
            person_str = listbox.get(index)
            name = person_str.split(' ')[0]

            for person in people:
                if person.name == name:
                    if messagebox.askyesno("确认删除", f"是否确认删除\"{name}\"？"):
                        people.remove(person)
                        break
                    else:
                        return

            listbox.delete(index)

    remove_person(listbox_offline)
    remove_person(listbox_online)
    remove_person(listbox_not_participating)
    save_people()
    refresh_listboxes()


def move_to_online():
    move_person(listbox_offline, listbox_online)


def move_to_onsite():
    move_person(listbox_online, listbox_offline)


def move_person(source_listbox, target_listbox):
    selected_indices = list(source_listbox.curselection())
    for index in sorted(selected_indices, reverse=True):
        person_str = source_listbox.get(index)
        name = person_str.split(' ')[0]

        for person in people:
            if person.name == name:
                person.location = "Online" if target_listbox == listbox_online else "On-site"
                break

        target_listbox.insert(tk.END, person_str)
        source_listbox.delete(index)

    save_people()


def exit_group():
    def exit_group_helper(listbox):
        selected_indices = list(listbox.curselection())
        for index in sorted(selected_indices, reverse=True):
            person_str = listbox.get(index)
            name = person_str.split(' ')[0]

            for person in people:
                if person.name == name:
                    not_participating_list.append(person)
                    people.remove(person)
                    break

            listbox_not_participating.insert(tk.END, person_str)
            listbox.delete(index)

    # On-site
    exit_group_helper(listbox_offline)
    # Online
    exit_group_helper(listbox_online)

    save_people()
    refresh_listboxes()


def join_group():
    selected_indices = list(listbox_not_participating.curselection())
    for index in sorted(selected_indices, reverse=True):
        person_str = listbox_not_participating.get(index)
        name = person_str.split(' ')[0]

        for person in not_participating_list:
            if person.name == name:
                people.append(person)
                not_participating_list.remove(person)
                break

        listbox_offline.insert(tk.END, person_str)
        listbox_not_participating.delete(index)

    save_people()
    refresh_listboxes()


def show_groups():
    num_groups = spinbox_groups.get()
    try:
        num_groups = int(num_groups)
    except ValueError:
        messagebox.showerror("输入错误", "组数必须为整数")
        return

    if len(people) < num_groups:
        messagebox.showerror("输入错误", "人数不足，无法分组")
        return
    groups = create_groups(num_groups)
    result = ""
    for i, group in enumerate(groups):
        result += f"Group {i + 1}:\n"
        for person in group:
            suffix = "*" if person.location == "Online" else ""
            result += f"  {person.name} ({person.gender}) {suffix}\n"
            # result += f"  {person.name} {suffix} \n"
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
        if abs(males - females) > 1:
            return False
    return True


young_people = ["羽菲", "朱睿", "云翼", "祖盈", "彦文"]
main_brothers = ["李尧", "常健", "志冬"]
family_chang = ["Joe", "Sue", "常健", "德琳"]


def separate_special_people(groups, names, max_number):
    for group in groups:
        count_group_special_names = sum([1 for person in group if person.name in names])
        if count_group_special_names > max_number:
            return False
    return True


def create_groups(num_groups):
    last_groups = load_last_groups()
    # print(last_groups)

    # 创建上次分组的映射，以便快速查询某人上次的组员
    last_group_map = {}
    for group in last_groups:
        for person_name in group:
            last_group_map[person_name] = set([p for p in group if p != person_name])
            # last_group_map[person_name] = set(group)
    print(last_group_map['云翼'])

    start = time.time()
    while True:
        random.shuffle(male_list)
        random.shuffle(female_list)
        groups = [[] for _ in range(num_groups)]

        for i, person in enumerate(male_list):
            groups[i % num_groups].append(person)
        i += 1
        for j, person in enumerate(female_list):
            groups[(i + j) % num_groups].append(person)

        # 检查每个组中是否有3个及以上的人在上一次分组中是同组的
        valid_groups = True
        for group in groups:
            # overlap_count = 0
            for person in group:
                if person.name in last_group_map:
                    overlap = last_group_map[person.name].intersection(set([p.name for p in group]))
                    if len(overlap) >= 3:  # 组内有3个或更多的重复成员
                        valid_groups = False
                        break
            if not valid_groups:
                break

        end = time.time()
        if valid_groups and separate_special_people(groups, main_brothers, 1) and separate_spouses(
                groups) and separate_special_people(
                groups, young_people, 2) and separate_special_people(groups, family_chang, 2):
            save_last_groups(groups)
            return groups
        elif (end - start) > 0.5:
            messagebox.showerror("错误", "不存在满足条件的分组情况")
            return


# 初始化人员列表
people = []
male_list = []
female_list = []
not_participating_list = []

# 创建主窗口
root = tk.Tk()
root.title("随机分组")

# 创建输入框和标签

label_name = tk.Label(root, text="姓名:")
label_name.grid(row=0, column=0, padx=10, pady=5)
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1, padx=10, pady=5, columnspan=2)

label_gender = tk.Label(root, text="性别:")
label_gender.grid(row=1, column=0, padx=10, pady=5)
var_gender = tk.StringVar(value="M")
radio_male = tk.Radiobutton(root, text="男", variable=var_gender, value="M")
radio_male.grid(row=1, column=1, padx=10, pady=5)
radio_female = tk.Radiobutton(root, text="女", variable=var_gender, value="F")
radio_female.grid(row=1, column=2, padx=10, pady=5)

label_location = tk.Label(root, text="地点:")
label_location.grid(row=2, column=0, padx=10, pady=5)
var_location = tk.StringVar(value="On-site")
radio_onsite = tk.Radiobutton(root, text="线下", variable=var_location, value="On-site")
radio_onsite.grid(row=2, column=1, padx=10, pady=5)
radio_online = tk.Radiobutton(root, text="线上", variable=var_location, value="Online")
radio_online.grid(row=2, column=2, padx=10, pady=5)

label_spouse = tk.Label(root, text="配偶:")
label_spouse.grid(row=3, column=0, padx=10, pady=5)
entry_spouse = tk.Entry(root)
entry_spouse.grid(row=3, column=1, padx=10, pady=5, columnspan=2)

label_groups = tk.Label(root, text="组数:")
label_groups.grid(row=9, column=0, padx=10, pady=5)
spinbox_groups = tk.Spinbox(root, from_=2, to=10, width=5)
spinbox_groups.grid(row=9, column=1, padx=10, pady=5, columnspan=2)
spinbox_groups.delete(0, "end")
spinbox_groups.insert(0, "3")

# 创建添加按钮
button_add = tk.Button(root, text="添加人员", command=add_person)
button_add.grid(row=4, column=0, padx=10, pady=5, columnspan=1)

# 创建删除按钮
button_delete = tk.Button(root, text="彻底删除", command=delete_person)
button_delete.grid(row=4, column=4, padx=10, pady=5)

# 创建退出分组按钮
button_exit_group = tk.Button(root, text="退出分组", command=exit_group)
button_exit_group.grid(row=6, column=2, padx=10, pady=5)

# 创建加入分组按钮
button_join_group = tk.Button(root, text="加入分组", command=join_group)
button_join_group.grid(row=6, column=4, padx=10, pady=5)

# 创建显示人员列表的列表框
listbox_offline = tk.Listbox(root, selectmode=tk.MULTIPLE, width=20, height=18)  # 允许多选并增加宽度和高度
listbox_offline.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

# 创建显示在线人员列表的列表框
listbox_online = tk.Listbox(root, selectmode=tk.MULTIPLE, width=20, height=18)  # 允许多选并增加宽度和高度
listbox_online.grid(row=8, column=2, columnspan=2, padx=10, pady=10)

label_online = tk.Label(root, text="Online")
label_online.grid(row=7, column=2, padx=10, pady=5)

label_onsite = tk.Label(root, text="On-site")
label_onsite.grid(row=7, column=0, padx=10, pady=5)

label_not_participating = tk.Label(root, text="Not Participating")
label_not_participating.grid(row=7, column=4, padx=10, pady=5)

# 创建显示不参与分组人员列表的列表框
listbox_not_participating = tk.Listbox(root, selectmode=tk.MULTIPLE, width=20, height=18)  # 允许多选并增加宽度和高度
listbox_not_participating.grid(row=8, column=4, columnspan=2, padx=10, pady=10)

button_move_to_online = tk.Button(root, text="转线上", command=move_to_online)
button_move_to_online.grid(row=6, column=0, padx=10, pady=5)

button_move_to_onsite = tk.Button(root, text="转线下", command=move_to_onsite)
button_move_to_onsite.grid(row=6, column=1, padx=10, pady=5)

# 创建分组按钮
button_group = tk.Button(root, text="随机分组", command=show_groups)
button_group.grid(row=11, column=2, padx=10, pady=5)

# 载入人员信息
load_people()

# 显示当前人数
label_current_count = tk.Label(root, text=f"当前人数：{len(people)}")
label_current_count.grid(row=10, column=2, padx=10, pady=5)

# 运行主循环
root.mainloop()
