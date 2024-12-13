from model import DB
from GUI import LoginWindow


def main():
    model = DB()
    model.create_tables()
    #model.initialize()

    view = LoginWindow(model)
    view.mainloop()


if __name__ == "__main__":
    main()
