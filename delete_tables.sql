delete from shopping_list;
delete from user_recipe;
delete from recipe_step;
delete from favorite_recipe;
delete from ingredient;
delete from current_meal;
delete from recipe;
commit;

drop table user_recipe;
drop table recipe_step;
drop table favorite_recipe;
drop table ingredient;
drop table current_meal;
drop table recipe;
drop table app_user;
drop table alembic_version;
commit;