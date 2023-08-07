import click, os, time


def register(app):        
    @app.cli.command()
    def addclass():
        """Add Classes to DB at scheduled interval"""
        print("Adding classes")
        time.sleep(5)
        print('Done')




