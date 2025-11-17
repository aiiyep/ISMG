from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL
            sql="""
                ALTER TABLE home_vagavoluntariado 
                ADD COLUMN IF NOT EXISTS vagas_ocupadas INTEGER DEFAULT 0 NOT NULL;
                
                UPDATE home_vagavoluntariado 
                SET vagas_ocupadas = 0 
                WHERE vagas_ocupadas IS NULL;
            """,
            # Reverse SQL (para rollback)
            reverse_sql="""
                ALTER TABLE home_vagavoluntariado 
                DROP COLUMN IF EXISTS vagas_ocupadas;
            """
        ),
    ]