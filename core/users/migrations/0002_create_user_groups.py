from django.db import migrations


def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    sales_group, _ = Group.objects.get_or_create(name="Sales")
    operations_group, _ = Group.objects.get_or_create(name="Operations")
    collections_group, _ = Group.objects.get_or_create(name="Collections")

    # Sales permissions
    client_content_type = ContentType.objects.get(app_label="clients", model="client")
    client_view_perm = Permission.objects.get(
        codename="view_client", content_type=client_content_type
    )
    client_add_perm = Permission.objects.get(
        codename="add_client", content_type=client_content_type
    )
    sales_group.permissions.add(client_view_perm, client_add_perm)

    # Operations permissions
    vehicle_content_type = ContentType.objects.get(
        app_label="vehicles", model="vehicle"
    )
    vehicle_view_perm = Permission.objects.get(
        codename="view_vehicle", content_type=vehicle_content_type
    )
    vehicle_add_perm = Permission.objects.get(
        codename="add_vehicle", content_type=vehicle_content_type
    )
    operations_group.permissions.add(vehicle_view_perm, vehicle_add_perm)

    # Collections permissions
    contracts_content_type = ContentType.objects.get(
        app_label="contracts", model="contract"
    )
    contracts_view_perm = Permission.objects.get(
        codename="view_contract", content_type=contracts_content_type
    )
    contracts_add_perm = Permission.objects.get(
        codename="add_contract", content_type=contracts_content_type
    )
    collections_group.permissions.add(contracts_view_perm, contracts_add_perm)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
        ("clients", "0001_initial"),
        ("vehicles", "0001_initial"),
        ("vehicles", "0002_vehiclebrand_alter_vehicle_brand_vehiclemodel_and_more"),
        ("contracts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]
