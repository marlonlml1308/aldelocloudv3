<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('products', function (Blueprint $table) {
            $table->engine = 'InnoDB';
            $table->charset = 'utf8mb4';
            $table->collation = 'utf8mb4_unicode_ci';
            $table->id();
            $table->string('menuitemtext');
            $table->unsignedBigInteger('menucategoryid');
            $table->unsignedBigInteger('menugroupid');
            $table->integer('displayindex');
            $table->decimal('defaultunitprice',total: 10, places: 2);
            $table->boolean('menuiteminactive',false);
            $table->boolean('menuiteminstock',true);
            $table->boolean('menuitemdiscountable',true);
            $table->string('menuitemtype');
            $table->string('menuitempopupheaderid')->nullable();
            $table->boolean('menuitemtaxable',false);
            $table->boolean('gstapplied',false);
            $table->boolean('liquortaxapplied',false);
            $table->string('gaspump');
            $table->boolean('bar',false);
            $table->string('barcode')->nullable();
            $table->decimal('dineinprice',total: 10, places: 2)->nullable();
            $table->decimal('takeoutprice',total: 10, places: 2)->nullable();
            $table->decimal('drivethruprice',total: 10, places: 2)->nullable();
            $table->decimal('DeliveryPrice',total: 10, places: 2)->nullable();
            $table->boolean('orderbyweight',false);
            $table->integer('qtycountdown')->nullable();
            $table->timestamps();
            $table->foreign('menucategoryid')->references('id')->on('categories')->onDelete('cascade');
            $table->foreign('menugroupid')->references('id')->on('groups')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('products');
    }
};
